import pymysql
from config import Config
from datetime import datetime


class NotificationLog:
    """通知日志模型"""

    def __init__(self, id=None, reminder_id=None, channel=None, status=None,
                 response=None, sent_at=None):
        self.id = id
        self.reminder_id = reminder_id
        self.channel = channel
        self.status = status
        self.response = response
        self.sent_at = sent_at

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
    def create(cls, reminder_id, channel, status, response=None):
        """创建日志记录"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO notification_logs
                    (reminder_id, channel, status, response)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (reminder_id, channel, status, response))
                log_id = cursor.lastrowid
            conn.commit()
            return log_id
        finally:
            conn.close()

    @classmethod
    def get_by_reminder_id(cls, reminder_id):
        """获取提醒的日志记录"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM notification_logs
                    WHERE reminder_id = %s
                    ORDER BY sent_at DESC
                """
                cursor.execute(sql, (reminder_id,))
                results = cursor.fetchall()
                return [cls(**row) for row in results]
        finally:
            conn.close()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'reminder_id': self.reminder_id,
            'channel': self.channel,
            'status': self.status,
            'response': self.response,
            'sent_at': str(self.sent_at) if self.sent_at else ''
        }
