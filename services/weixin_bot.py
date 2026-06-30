import requests
import json
from datetime import datetime


class WeixinBot:
    """微信企业微信机器人推送服务"""

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        """发送文本消息"""
        message = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

        if mentioned_list:
            message["text"]["mentioned_list"] = mentioned_list
        if mentioned_mobile_list:
            message["text"]["mentioned_mobile_list"] = mentioned_mobile_list

        return self._send(message)

    def send_markdown(self, content):
        """发送markdown消息"""
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        return self._send(message)

    def send_news(self, title, description, url, picurl=None):
        """发送图文消息"""
        article = {
            "title": title,
            "description": description,
            "url": url
        }
        if picurl:
            article["picurl"] = picurl

        message = {
            "msgtype": "news",
            "news": {
                "articles": [article]
            }
        }
        return self._send(message)

    def send_reminder(self, reminder, memo):
        """发送提醒消息"""
        title = f"⏰ 家庭提醒：{reminder.title or memo.title}"

        content_parts = [f"# {title}\n"]

        if memo.content:
            content_parts.append(f"**内容：**\n{memo.content}\n")

        if memo.member_name:
            content_parts.append(f"**关联家人：**{memo.member_name}\n")

        if reminder.remind_at:
            content_parts.append(f"**提醒时间：**{reminder.remind_at}\n")

        if reminder.repeat_type and reminder.repeat_type != 'none':
            repeat_labels = {
                'daily': '每天',
                'weekly': '每周',
                'monthly': '每月',
                'yearly': '每年'
            }
            content_parts.append(f"**重复：**{repeat_labels.get(reminder.repeat_type, reminder.repeat_type)}\n")

        content_parts.append(f"\n> 发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        content = "\n".join(content_parts)

        # 企业微信机器人支持markdown
        return self.send_markdown(content)

    def _send(self, message):
        """发送消息到企业微信"""
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

            if result.get('errcode') == 0:
                return {
                    'success': True,
                    'message': '发送成功',
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': result.get('errmsg', '发送失败'),
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

        if not webhook_url.startswith('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='):
            return False, "webhook地址格式不正确"

        return True, "格式正确"


class WeixinMP:
    """微信公众号模板消息（需要认证，较复杂）"""

    def __init__(self, appid, appsecret, template_id):
        self.appid = appid
        self.appsecret = appsecret
        self.template_id = template_id
        self.access_token = None
        self.token_expires = 0

    def _get_access_token(self):
        """获取access_token"""
        import time

        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"

        try:
            response = requests.get(url, timeout=30)
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                self.token_expires = time.time() + result.get('expires_in', 7200) - 300
                return self.access_token
            else:
                return None
        except:
            return None

    def send_template_message(self, openid, data, url=None):
        """发送模板消息"""
        access_token = self._get_access_token()
        if not access_token:
            return {'success': False, 'message': '获取access_token失败'}

        template_data = {
            "touser": openid,
            "template_id": self.template_id,
            "data": data
        }

        if url:
            template_data["url"] = url

        api_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"

        try:
            response = requests.post(
                api_url,
                data=json.dumps(template_data),
                timeout=30
            )
            result = response.json()

            if result.get('errcode') == 0:
                return {'success': True, 'message': '发送成功'}
            else:
                return {'success': False, 'message': result.get('errmsg', '发送失败')}
        except Exception as e:
            return {'success': False, 'message': str(e)}
