import requests
import json
from datetime import datetime


class FeishuBot:
    """飞书机器人推送服务"""

    def __init__(self, webhook_url, secret=None):
        self.webhook_url = webhook_url
        self.secret = secret

    def send_text(self, title, content, at_all=False):
        """发送文本消息"""
        message = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n\n{content}"
            }
        }

        if at_all:
            message["content"]["text"] += "\n\n@所有人"

        return self._send(message)

    def send_card(self, title, content, memo_link=None):
        """发送卡片消息（更美观）"""
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        if memo_link:
            elements.insert(1, {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看详情"
                        },
                        "type": "primary",
                        "url": memo_link
                    }
                ]
            })

        message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }

        return self._send(message)

    def send_reminder(self, reminder, memo):
        """发送提醒消息"""
        title = f"😊 温馨提醒：{memo.title}"

        content_parts = []
        if memo.content:
            content_parts.append(f"**内容：**\n{memo.content}")

        if memo.member_name:
            content_parts.append(f"\n**关联家人：**{memo.member_name}")

        if reminder.repeat_type and reminder.repeat_type != 'none':
            repeat_labels = {
                'daily': '每天',
                'weekly': '每周',
                'monthly': '每月',
                'yearly': '每年'
            }
            content_parts.append(f"\n**重复：**{repeat_labels.get(reminder.repeat_type, reminder.repeat_type)}")

        content = "\n".join(content_parts)

        return self.send_card(title, content)

    def _send(self, message):
        """发送消息到飞书"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(message),
                timeout=30
            )

            result = response.json()

            if result.get('code') == 0:
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

    @classmethod
    def validate_webhook(cls, webhook_url):
        """验证webhook地址是否有效"""
        if not webhook_url:
            return False, "webhook地址不能为空"

        if not webhook_url.startswith('https://open.feishu.cn/open-apis/bot/v2/hook/'):
            return False, "webhook地址格式不正确"

        return True, "格式正确"
