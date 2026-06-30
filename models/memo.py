import pymysql
from config import Config
from datetime import datetime


class Memo:
    """备忘录模型"""

    def __init__(self, id=None, title=None, content=None, family_member_id=None,
                 category='life', priority='normal', status='active',
                 created_at=None, updated_at=None, member_name=None):
        self.id = id
        self.title = title
        self.content = content
        self.family_member_id = family_member_id
        self.category = category
        self.priority = priority
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.member_name = member_name  # 关联查询用

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
    def get_all(cls, search=None, category=None, member_id=None, status='active'):
        """获取备忘录列表"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT m.*, fm.name as member_name
                    FROM memos m
                    LEFT JOIN family_members fm ON m.family_member_id = fm.id
                    WHERE m.status = %s
                """
                params = [status]

                if search:
                    sql += " AND (m.title LIKE %s OR m.content LIKE %s)"
                    params.extend([f'%{search}%', f'%{search}%'])

                if category:
                    sql += " AND m.category = %s"
                    params.append(category)

                if member_id:
                    sql += " AND m.family_member_id = %s"
                    params.append(member_id)

                sql += " ORDER BY m.created_at DESC"

                cursor.execute(sql, params)
                results = cursor.fetchall()
                return [cls(**row) for row in results]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, memo_id):
        """根据ID获取备忘录"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT m.*, fm.name as member_name
                    FROM memos m
                    LEFT JOIN family_members fm ON m.family_member_id = fm.id
                    WHERE m.id = %s
                """
                cursor.execute(sql, (memo_id,))
                result = cursor.fetchone()
                return cls(**result) if result else None
        finally:
            conn.close()

    def save(self):
        """保存备忘录"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                if self.id:
                    # 更新
                    sql = """
                        UPDATE memos SET
                            title = %s, content = %s, family_member_id = %s,
                            category = %s, priority = %s, status = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        self.title, self.content, self.family_member_id,
                        self.category, self.priority, self.status, self.id
                    ))
                else:
                    # 新增
                    sql = """
                        INSERT INTO memos
                        (title, content, family_member_id, category, priority, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        self.title, self.content, self.family_member_id,
                        self.category, self.priority, self.status
                    ))
                    self.id = cursor.lastrowid
            conn.commit()
            return self.id
        finally:
            conn.close()

    @classmethod
    def delete_by_id(cls, memo_id):
        """软删除备忘录"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE memos SET status = 'deleted' WHERE id = %s"
                cursor.execute(sql, (memo_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'family_member_id': self.family_member_id,
            'member_name': self.member_name,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else '',
            'updated_at': str(self.updated_at) if self.updated_at else ''
        }

    @classmethod
    def get_categories(cls):
        """获取分类列表"""
        return [
            {'value': 'life', 'label': '生活'},
            {'value': 'medical', 'label': '医疗'},
            {'value': 'education', 'label': '教育'},
            {'value': 'work', 'label': '工作'},
            {'value': 'other', 'label': '其他'}
        ]

    @classmethod
    def get_priorities(cls):
        """获取优先级列表"""
        return [
            {'value': 'low', 'label': '低'},
            {'value': 'normal', 'label': '中'},
            {'value': 'high', 'label': '高'}
        ]
