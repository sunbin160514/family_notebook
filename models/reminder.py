import pymysql
import json
from config import Config
from datetime import datetime, timedelta


class Reminder:
    """提醒模型"""

    def __init__(self, id=None, memo_id=None, title=None, remind_at=None,
                 repeat_type='none', repeat_end_date=None, notify_channels=None,
                 status='pending', last_sent_at=None, created_at=None,
                 memo_title=None):
        self.id = id
        self.memo_id = memo_id
        self.title = title
        self.remind_at = remind_at
        self.repeat_type = repeat_type
        self.repeat_end_date = repeat_end_date
        self.notify_channels = notify_channels or ['feishu']
        self.status = status
        self.last_sent_at = last_sent_at
        self.created_at = created_at
        self.memo_title = memo_title  # 关联查询用

    @classmethod
    def get_db_connection(cls):
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn

    @classmethod
    def get_pending_reminders(cls, before_time=None):
        """获取待发送的提醒"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                if before_time is None:
                    before_time = datetime.now()

                sql = """
                    SELECT r.*, m.title as memo_title
                    FROM reminders r
                    JOIN memos m ON r.memo_id = m.id
                    WHERE r.status = 'pending'
                    AND r.remind_at <= %s
                    AND (r.repeat_end_date IS NULL OR r.repeat_end_date >= %s)
                """
                cursor.execute(sql, (before_time, before_time.date()))
                results = cursor.fetchall()

                # 解析JSON字段
                for row in results:
                    if row.get('notify_channels'):
                        try:
                            row['notify_channels'] = json.loads(row['notify_channels'])
                        except:
                            row['notify_channels'] = ['feishu']

                return [cls(**row) for row in results]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, reminder_id):
        """根据ID获取提醒"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT r.*, m.title as memo_title
                    FROM reminders r
                    JOIN memos m ON r.memo_id = m.id
                    WHERE r.id = %s
                """
                cursor.execute(sql, (reminder_id,))
                result = cursor.fetchone()

                if result and result.get('notify_channels'):
                    try:
                        result['notify_channels'] = json.loads(result['notify_channels'])
                    except:
                        result['notify_channels'] = ['feishu']

                return cls(**result) if result else None
        finally:
            conn.close()

    @classmethod
    def get_by_memo_id(cls, memo_id):
        """根据备忘录ID获取提醒列表"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT r.*, m.title as memo_title
                    FROM reminders r
                    JOIN memos m ON r.memo_id = m.id
                    WHERE r.memo_id = %s
                    ORDER BY r.remind_at ASC
                """
                cursor.execute(sql, (memo_id,))
                results = cursor.fetchall()

                for row in results:
                    if row.get('notify_channels'):
                        try:
                            row['notify_channels'] = json.loads(row['notify_channels'])
                        except:
                            row['notify_channels'] = ['feishu']

                return [cls(**row) for row in results]
        finally:
            conn.close()

    def save(self):
        """保存提醒"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 序列化notify_channels
                channels_json = json.dumps(self.notify_channels) if isinstance(self.notify_channels, list) else self.notify_channels

                if self.id:
                    # 更新
                    sql = """
                        UPDATE reminders SET
                            title = %s, remind_at = %s, repeat_type = %s,
                            repeat_end_date = %s, notify_channels = %s, status = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        self.title, self.remind_at, self.repeat_type,
                        self.repeat_end_date, channels_json, self.status, self.id
                    ))
                else:
                    # 新增
                    sql = """
                        INSERT INTO reminders
                        (memo_id, title, remind_at, repeat_type, repeat_end_date, notify_channels, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        self.memo_id, self.title, self.remind_at, self.repeat_type,
                        self.repeat_end_date, channels_json, self.status
                    ))
                    self.id = cursor.lastrowid
            conn.commit()
            return self.id
        finally:
            conn.close()

    def mark_as_sent(self):
        """标记为已发送"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE reminders
                    SET status = 'sent', last_sent_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(sql, (self.id,))
            conn.commit()

            # 如果是重复提醒，创建下一次提醒
            if self.repeat_type != 'none':
                self._schedule_next()

            return True
        finally:
            conn.close()

    def _schedule_next(self):
        """计算并创建下一次重复提醒"""
        if self.repeat_type == 'none':
            return

        # 计算下一次提醒时间
        current_remind_at = self.remind_at
        if isinstance(current_remind_at, str):
            current_remind_at = datetime.strptime(current_remind_at, '%Y-%m-%d %H:%M:%S')

        if self.repeat_type == 'daily':
            next_remind_at = current_remind_at + timedelta(days=1)
        elif self.repeat_type == 'weekly':
            next_remind_at = current_remind_at + timedelta(weeks=1)
        elif self.repeat_type == 'monthly':
            # 简单处理：加30天
            next_remind_at = current_remind_at + timedelta(days=30)
        elif self.repeat_type == 'yearly':
            # 简单处理：加365天
            next_remind_at = current_remind_at + timedelta(days=365)
        else:
            return

        # 检查是否超过结束日期
        if self.repeat_end_date:
            end_date = self.repeat_end_date
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if next_remind_at.date() > end_date:
                return

        # 创建新的提醒
        new_reminder = Reminder(
            memo_id=self.memo_id,
            title=self.title,
            remind_at=next_remind_at,
            repeat_type=self.repeat_type,
            repeat_end_date=self.repeat_end_date,
            notify_channels=self.notify_channels,
            status='pending'
        )
        new_reminder.save()

    @classmethod
    def delete_by_id(cls, reminder_id):
        """删除提醒"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM reminders WHERE id = %s"
                cursor.execute(sql, (reminder_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'memo_id': self.memo_id,
            'memo_title': self.memo_title,
            'title': self.title,
            'remind_at': str(self.remind_at) if self.remind_at else '',
            'repeat_type': self.repeat_type,
            'repeat_end_date': str(self.repeat_end_date) if self.repeat_end_date else '',
            'notify_channels': self.notify_channels,
            'status': self.status,
            'last_sent_at': str(self.last_sent_at) if self.last_sent_at else '',
            'created_at': str(self.created_at) if self.created_at else ''
        }

    @classmethod
    def get_repeat_types(cls):
        """获取重复类型列表"""
        return [
            {'value': 'none', 'label': '不重复'},
            {'value': 'daily', 'label': '每天'},
            {'value': 'weekly', 'label': '每周'},
            {'value': 'monthly', 'label': '每月'},
            {'value': 'yearly', 'label': '每年'}
        ]
