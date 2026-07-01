import requests
import json
from datetime import datetime


class PushPlus:
    """PushPlus 微信推送服务

    使用文档: https://www.pushplus.plus/doc/
    """

    API_URL = 'http://www.pushplus.plus/send'

    def __init__(self, token):
        self.token = token

    def send(self, title, content, template='html'):
        """发送消息

        Args:
            title: 消息标题
            content: 消息内容
            template: 消息模板 (html/json/txt/markdown)
        """
        if not self.token:
            return {
                'success': False,
                'message': 'PushPlus Token 未配置'
            }

        try:
            data = {
                'token': self.token,
                'title': title,
                'content': content,
                'template': template
            }

            response = requests.post(
                self.API_URL,
                data=data,
                timeout=30
            )

            result = response.json()

            if result.get('code') == 200:
                return {
                    'success': True,
                    'message': '发送成功',
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': result.get('msg', '发送失败'),
                    'data': result
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'发送异常：{str(e)}',
                'data': None
            }

    def send_reminder(self, reminder, memo):
        """发送提醒消息"""
        title = f"😊 温馨提醒：{memo.title}"

        content_parts = []
        if memo.content:
            content_parts.append(f"<p><strong>内容：</strong></p>")
            content_parts.append(f"<p>{memo.content}</p>")

        if memo.member_name:
            content_parts.append(f"<p><strong>关联家人：</strong>{memo.member_name}</p>")

        if reminder.repeat_type and reminder.repeat_type != 'none':
            repeat_labels = {
                'daily': '每天',
                'weekly': '每周',
                'monthly': '每月',
                'yearly': '每年'
            }
            content_parts.append(f"<p><strong>重复：</strong>{repeat_labels.get(reminder.repeat_type, reminder.repeat_type)}</p>")

        content_parts.append(f"<p style='color:#999;font-size:12px;margin-top:15px;'>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

        content = "\n".join(content_parts)

        return self.send(title, content, template='html')

    def send_simple(self, title, content):
        """发送简单文本消息"""
        return self.send(title, content, template='txt')

    @classmethod
    def validate_token(cls, token):
        """验证 Token 格式"""
        if not token:
            return False, "PushPlus Token 不能为空"

        if len(token) < 10:
            return False, "Token 格式不正确"

        return True, "格式正确"
