import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import requests

from models.reminder import Reminder
from models.memo import Memo
from models.system_setting import SystemSetting
from models.notification_log import NotificationLog
from services.feishu_bot import FeishuBot
from services.weixin_bot import WeixinBot
from services.pushplus import PushPlus


class ReminderScheduler:
    """提醒调度器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scheduler = None
        return cls._instance

    def init_scheduler(self):
        """初始化调度器"""
        if self.scheduler is None:
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(
                func=self.check_and_send_reminders,
                trigger=CronTrigger(minute='*'),  # 每分钟检查一次
                id='reminder_job',
                name='检查并发送提醒',
                replace_existing=True
            )
            print(f"[{datetime.now()}] 提醒调度器已初始化")

    def start(self):
        """启动调度器"""
        self.init_scheduler()
        if not self.scheduler.running:
            self.scheduler.start()
            print(f"[{datetime.now()}] 提醒调度器已启动")

    def shutdown(self):
        """停止调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            print(f"[{datetime.now()}] 提醒调度器已停止")

    def check_and_send_reminders(self):
        """检查并发送提醒"""
        try:
            print(f"[{datetime.now()}] 检查待发送提醒...")

            # 检查是否启用通知
            settings = SystemSetting.get_notification_settings()
            if not settings.get('notification_enabled'):
                print("通知功能已禁用")
                return

            # 获取待发送的提醒
            now = datetime.now()
            reminders = Reminder.get_pending_reminders(before_time=now)

            if not reminders:
                print("没有待发送的提醒")
                return

            print(f"找到 {len(reminders)} 条待发送提醒")

            for reminder in reminders:
                self._send_reminder(reminder, settings)

        except Exception as e:
            print(f"检查提醒时出错：{str(e)}")

    def _send_reminder(self, reminder, settings):
        """发送单个提醒"""
        try:
            # 获取关联的备忘录
            memo = Memo.get_by_id(reminder.memo_id)
            if not memo:
                print(f"提醒 {reminder.id} 关联的备忘录不存在")
                return

            # 发送消息到各渠道
            channels = reminder.notify_channels or ['feishu']

            for channel in channels:
                if channel == 'feishu':
                    self._send_feishu(reminder, memo, settings)
                elif channel == 'weixin':
                    self._send_weixin(reminder, memo, settings)
                elif channel == 'pushplus':
                    self._send_pushplus(reminder, memo, settings)

            # 标记为已发送
            reminder.mark_as_sent()
            print(f"提醒 {reminder.id} 已处理")

        except Exception as e:
            print(f"发送提醒 {reminder.id} 失败：{str(e)}")

    def _send_feishu(self, reminder, memo, settings):
        """发送到飞书"""
        webhook_url = settings.get('feishu_webhook_url')
        secret = settings.get('feishu_secret')

        if not webhook_url:
            print("飞书webhook未配置")
            return

        bot = FeishuBot(webhook_url, secret)
        result = bot.send_reminder(reminder, memo)

        # 记录日志
        NotificationLog.create(
            reminder_id=reminder.id,
            channel='feishu',
            status='success' if result['success'] else 'failed',
            response=str(result.get('data', ''))[:500]
        )

        print(f"飞书发送结果：{result['message']}")

    def _send_weixin(self, reminder, memo, settings):
        """发送到微信"""
        webhook_url = settings.get('weixin_webhook_url')

        if not webhook_url:
            print("微信webhook未配置")
            return

        bot = WeixinBot(webhook_url)
        result = bot.send_reminder(reminder, memo)

        # 记录日志
        NotificationLog.create(
            reminder_id=reminder.id,
            channel='weixin',
            status='success' if result['success'] else 'failed',
            response=str(result.get('data', ''))[:500]
        )

        print(f"微信发送结果：{result['message']}")

    def _send_pushplus(self, reminder, memo, settings):
        """发送到 PushPlus（个人微信）"""
        token = settings.get('pushplus_token')

        if not token:
            print("PushPlus Token 未配置")
            return

        bot = PushPlus(token)
        result = bot.send_reminder(reminder, memo)

        # 记录日志
        NotificationLog.create(
            reminder_id=reminder.id,
            channel='pushplus',
            status='success' if result['success'] else 'failed',
            response=str(result.get('data', ''))[:500]
        )

        print(f"PushPlus 发送结果：{result['message']}")


# 全局调度器实例
scheduler = ReminderScheduler()


def start_scheduler():
    """启动调度器（供外部调用）"""
    scheduler.start()


def shutdown_scheduler():
    """停止调度器"""
    scheduler.shutdown()


if __name__ == '__main__':
    # 测试运行
    start_scheduler()
    try:
        # 保持运行
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        shutdown_scheduler()
