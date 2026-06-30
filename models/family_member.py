import pymysql
from config import Config
from datetime import datetime, timedelta


class FamilyMember:
    """家人信息模型"""

    def __init__(self, id=None, name=None, nickname=None, solar_birthday=None,
                 lunar_birthday=None, favorite_foods=None, favorite_sports=None,
                 disliked_foods=None, daily_notes=None, remarks=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.nickname = nickname
        self.solar_birthday = solar_birthday
        self.lunar_birthday = lunar_birthday
        self.favorite_foods = favorite_foods
        self.favorite_sports = favorite_sports
        self.disliked_foods = disliked_foods
        self.daily_notes = daily_notes
        self.remarks = remarks
        self.created_at = created_at
        self.updated_at = updated_at

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
    def get_all(cls, search=None):
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                if search:
                    sql = """
                        SELECT * FROM family_members
                        WHERE name LIKE %s OR nickname LIKE %s
                        ORDER BY name ASC
                    """
                    cursor.execute(sql, (f'%{search}%', f'%{search}%'))
                else:
                    sql = "SELECT * FROM family_members ORDER BY name ASC"
                    cursor.execute(sql)
                results = cursor.fetchall()
                return [cls(**row) for row in results]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, member_id):
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM family_members WHERE id = %s"
                cursor.execute(sql, (member_id,))
                result = cursor.fetchone()
                return cls(**result) if result else None
        finally:
            conn.close()

    def save(self):
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                if self.id:
                    # 更新
                    sql = """
                        UPDATE family_members SET
                            name = %s, nickname = %s, solar_birthday = %s, lunar_birthday = %s,
                            favorite_foods = %s, favorite_sports = %s, disliked_foods = %s,
                            daily_notes = %s, remarks = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        self.name, self.nickname, self.solar_birthday, self.lunar_birthday,
                        self.favorite_foods, self.favorite_sports, self.disliked_foods,
                        self.daily_notes, self.remarks, self.id
                    ))
                else:
                    # 新增
                    sql = """
                        INSERT INTO family_members
                        (name, nickname, solar_birthday, lunar_birthday, favorite_foods,
                         favorite_sports, disliked_foods, daily_notes, remarks)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        self.name, self.nickname, self.solar_birthday, self.lunar_birthday,
                        self.favorite_foods, self.favorite_sports, self.disliked_foods,
                        self.daily_notes, self.remarks
                    ))
                    self.id = cursor.lastrowid
            conn.commit()
            return self.id
        finally:
            conn.close()

    @classmethod
    def delete_by_id(cls, member_id):
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM family_members WHERE id = %s"
                cursor.execute(sql, (member_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def get_all_for_export(cls):
        """获取所有数据用于导出"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM family_members ORDER BY id ASC"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def get_birthday_reminders(cls, days=7):
        """获取即将到来的生日提醒"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                today = datetime.now().date()
                reminders = []

                sql = "SELECT * FROM family_members WHERE solar_birthday IS NOT NULL"
                cursor.execute(sql)
                members = cursor.fetchall()

                for member in members:
                    birthday = member['solar_birthday']
                    if birthday:
                        # 计算今年生日
                        this_year_birthday = birthday.replace(year=today.year)
                        if this_year_birthday < today:
                            this_year_birthday = birthday.replace(year=today.year + 1)

                        days_until = (this_year_birthday - today).days
                        if 0 <= days_until <= days:
                            member['days_until'] = days_until
                            reminders.append(member)

                # 按天数排序
                reminders.sort(key=lambda x: x['days_until'])
                return reminders
        finally:
            conn.close()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'solar_birthday': str(self.solar_birthday) if self.solar_birthday else '',
            'lunar_birthday': self.lunar_birthday,
            'favorite_foods': self.favorite_foods,
            'favorite_sports': self.favorite_sports,
            'disliked_foods': self.disliked_foods,
            'daily_notes': self.daily_notes,
            'remarks': self.remarks,
            'created_at': str(self.created_at) if self.created_at else '',
            'updated_at': str(self.updated_at) if self.updated_at else ''
        }
