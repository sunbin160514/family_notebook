import pymysql
from config import Config


class SystemSetting:
    """系统设置模型"""

    # 默认配置
    DEFAULTS = {
        'feishu_webhook_url': '',
        'feishu_secret': '',
        'weixin_webhook_url': '',
        'notification_enabled': 'true'
    }

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
    def get(cls, key, default=None):
        """获取设置值"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT setting_value FROM system_settings WHERE setting_key = %s"
                cursor.execute(sql, (key,))
                result = cursor.fetchone()

                if result:
                    return result['setting_value']
                else:
                    return default or cls.DEFAULTS.get(key, '')
        finally:
            conn.close()

    @classmethod
    def set(cls, key, value, description=None):
        """设置值"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 检查是否存在
                sql_check = "SELECT id FROM system_settings WHERE setting_key = %s"
                cursor.execute(sql_check, (key,))
                existing = cursor.fetchone()

                if existing:
                    sql = "UPDATE system_settings SET setting_value = %s WHERE setting_key = %s"
                    cursor.execute(sql, (value, key))
                else:
                    sql = """
                        INSERT INTO system_settings (setting_key, setting_value, description)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (key, value, description))
            conn.commit()
            return True
        finally:
            conn.close()

    @classmethod
    def get_all(cls):
        """获取所有设置"""
        conn = cls.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT setting_key, setting_value, description FROM system_settings"
                cursor.execute(sql)
                results = cursor.fetchall()

                # 转换为字典
                settings = {row['setting_key']: row['setting_value'] for row in results}

                # 填充默认值
                for key, value in cls.DEFAULTS.items():
                    if key not in settings:
                        settings[key] = value

                return settings
        finally:
            conn.close()

    @classmethod
    def get_notification_settings(cls):
        """获取通知相关配置"""
        return {
            'feishu_webhook_url': cls.get('feishu_webhook_url'),
            'feishu_secret': cls.get('feishu_secret'),
            'weixin_webhook_url': cls.get('weixin_webhook_url'),
            'notification_enabled': cls.get('notification_enabled') == 'true'
        }

    @classmethod
    def save_notification_settings(cls, data):
        """保存通知配置"""
        settings = [
            ('feishu_webhook_url', data.get('feishu_webhook_url', ''), '飞书机器人Webhook'),
            ('feishu_secret', data.get('feishu_secret', ''), '飞书机器人Secret'),
            ('weixin_webhook_url', data.get('weixin_webhook_url', ''), '微信机器人Webhook'),
            ('notification_enabled', 'true' if data.get('notification_enabled') else 'false', '是否启用通知')
        ]

        for key, value, desc in settings:
            cls.set(key, value, desc)

        return True
