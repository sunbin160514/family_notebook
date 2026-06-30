from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import atexit

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.family_member import FamilyMember
from models.memo import Memo
from models.reminder import Reminder
from models.system_setting import SystemSetting
from services.scheduler import start_scheduler, shutdown_scheduler
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JSON_AS_ASCII'] = False
app.config['JSON_ENSURE_ASCII'] = False

# 启用CORS，允许前端跨域访问
# 从环境变量获取前端URL，默认为本地开发地址
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173", frontend_url]

CORS(app, resources={
    r"/api/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 启动提醒调度器
start_scheduler()
atexit.register(shutdown_scheduler)


@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """删除家人"""
    if FamilyMember.delete_by_id(member_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


@app.route('/api/members/<int:member_id>/delete', methods=['GET'])
def delete_member_get(member_id):
    """删除家人 - GET方式"""
    if FamilyMember.delete_by_id(member_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


@app.route('/api/members', methods=['GET'])
def api_get_members():
    """API - 获取所有家人列表"""
    search = request.args.get('search', '').strip()
    members = FamilyMember.get_all(search=search if search else None)
    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in members],
        'count': len(members)
    })


@app.route('/api/members/<int:member_id>', methods=['GET'])
def api_get_member(member_id):
    """API - 获取单个家人详情"""
    member = FamilyMember.get_by_id(member_id)
    if not member:
        return jsonify({'success': False, 'message': '家人不存在'}), 404
    return jsonify({
        'success': True,
        'data': member.to_dict()
    })


@app.route('/api/members', methods=['POST'])
def api_add_member():
    """API - 新增家人"""
    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'message': '姓名不能为空'}), 400

    member = FamilyMember(
        name=name,
        nickname=data.get('nickname'),
        solar_birthday=data.get('solar_birthday') or None,
        lunar_birthday=data.get('lunar_birthday'),
        favorite_foods=data.get('favorite_foods'),
        favorite_sports=data.get('favorite_sports'),
        disliked_foods=data.get('disliked_foods'),
        daily_notes=data.get('daily_notes'),
        remarks=data.get('remarks')
    )
    member.save()

    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': member.to_dict()
    })


@app.route('/api/members/<int:member_id>/update', methods=['GET', 'POST'])
def api_update_member(member_id):
    """API - 更新家人信息"""
    member = FamilyMember.get_by_id(member_id)
    if not member:
        return jsonify({'success': False, 'message': '家人不存在'}), 404

    # 支持GET请求（查询参数）和POST请求（JSON或表单）
    if request.method == 'POST':
        data = request.get_json() or request.form
    else:
        data = request.args

    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    # 更新字段
    if 'name' in data:
        member.name = data.get('name')
    if 'nickname' in data:
        member.nickname = data.get('nickname')
    if 'solar_birthday' in data:
        member.solar_birthday = data.get('solar_birthday') or None
    if 'lunar_birthday' in data:
        member.lunar_birthday = data.get('lunar_birthday')
    if 'favorite_foods' in data:
        member.favorite_foods = data.get('favorite_foods')
    if 'favorite_sports' in data:
        member.favorite_sports = data.get('favorite_sports')
    if 'disliked_foods' in data:
        member.disliked_foods = data.get('disliked_foods')
    if 'daily_notes' in data:
        member.daily_notes = data.get('daily_notes')
    if 'remarks' in data:
        member.remarks = data.get('remarks')

    member.save()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': member.to_dict()
    })


@app.route('/api/export')
def export_data():
    """导出Excel数据"""
    wb = Workbook()
    ws = wb.active
    ws.title = "家人信息"

    # 设置表头
    headers = ['ID', '姓名', '昵称', '阳历生日', '阴历生日', '喜欢的食物',
               '喜欢的运动', '讨厌的食物', '日常注意事项', '备注', '创建时间', '更新时间']
    ws.append(headers)

    # 设置列宽
    column_widths = [8, 12, 12, 12, 12, 25, 25, 25, 30, 25, 18, 18]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + i)].width = width

    # 获取数据
    members = FamilyMember.get_all_for_export()

    # 填充数据
    for member in members:
        ws.append([
            member['id'],
            member['name'],
            member['nickname'] or '',
            str(member['solar_birthday']) if member['solar_birthday'] else '',
            member['lunar_birthday'] or '',
            member['favorite_foods'] or '',
            member['favorite_sports'] or '',
            member['disliked_foods'] or '',
            member['daily_notes'] or '',
            member['remarks'] or '',
            str(member['created_at']) if member['created_at'] else '',
            str(member['updated_at']) if member['updated_at'] else ''
        ])

    # 保存到内存
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f'family_members_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return send_file(output, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'service': 'family_notebook'})


# ============================================
# 备忘录模块 API
# ============================================

@app.route('/api/memos', methods=['GET'])
def api_get_memos():
    """API - 获取备忘录列表"""
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    member_id = request.args.get('member_id', type=int)

    memos = Memo.get_all(
        search=search if search else None,
        category=category if category else None,
        member_id=member_id
    )

    # 获取每个备忘录的提醒信息
    result = []
    for memo in memos:
        memo_dict = memo.to_dict()
        memo_dict['reminders'] = [r.to_dict() for r in Reminder.get_by_memo_id(memo.id)]
        result.append(memo_dict)

    return jsonify({
        'success': True,
        'data': result,
        'count': len(result)
    })


@app.route('/api/memos', methods=['POST'])
def api_add_memo():
    """API - 新增备忘录（支持同时创建提醒）"""
    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'success': False, 'message': '标题不能为空'}), 400

    memo = Memo(
        title=title,
        content=data.get('content'),
        family_member_id=data.get('family_member_id') or None,
        category=data.get('category', 'life'),
        priority=data.get('priority', 'normal'),
        status='active'
    )
    memo.save()

    # 重新查询获取完整数据（包括 created_at）
    memo = Memo.get_by_id(memo.id)

    # 如果设置了提醒时间，创建提醒
    created_reminder = None
    remind_at = data.get('remind_at')
    if remind_at:
        reminder = Reminder(
            memo_id=memo.id,
            title=f'📋 {title}',
            remind_at=remind_at,
            repeat_type=data.get('repeat_type', 'none'),
            repeat_end_date=data.get('repeat_end_date') or None,
            notify_channels=data.get('notify_channels', ['feishu']),
            status='pending'
        )
        reminder.save()
        created_reminder = reminder

    # 组装返回数据（包含提醒信息）
    result = memo.to_dict()
    result['reminders'] = [created_reminder.to_dict()] if created_reminder else []

    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': result
    })


@app.route('/api/memos/<int:memo_id>', methods=['GET'])
def api_get_memo(memo_id):
    """API - 获取备忘录详情"""
    memo = Memo.get_by_id(memo_id)
    if not memo:
        return jsonify({'success': False, 'message': '备忘录不存在'}), 404

    memo_dict = memo.to_dict()
    memo_dict['reminders'] = [r.to_dict() for r in Reminder.get_by_memo_id(memo_id)]

    return jsonify({
        'success': True,
        'data': memo_dict
    })


@app.route('/api/memos/<int:memo_id>', methods=['PUT', 'POST'])
def api_update_memo(memo_id):
    """API - 更新备忘录"""
    memo = Memo.get_by_id(memo_id)
    if not memo:
        return jsonify({'success': False, 'message': '备忘录不存在'}), 404

    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    if 'title' in data:
        memo.title = data.get('title')
    if 'content' in data:
        memo.content = data.get('content')
    if 'family_member_id' in data:
        memo.family_member_id = data.get('family_member_id') or None
    if 'category' in data:
        memo.category = data.get('category')
    if 'priority' in data:
        memo.priority = data.get('priority')
    if 'status' in data:
        memo.status = data.get('status')

    memo.save()

    # 组装返回数据（包含提醒信息）
    result = memo.to_dict()
    result['reminders'] = [r.to_dict() for r in Reminder.get_by_memo_id(memo_id)]

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': result
    })


@app.route('/api/memos/<int:memo_id>', methods=['DELETE'])
def api_delete_memo(memo_id):
    """API - 删除备忘录"""
    if Memo.delete_by_id(memo_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


@app.route('/api/memos/<int:memo_id>/delete', methods=['GET'])
def api_delete_memo_get(memo_id):
    """API - 删除备忘录 (GET方式)"""
    if Memo.delete_by_id(memo_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


# ============================================
# 提醒模块 API
# ============================================

@app.route('/api/reminders', methods=['GET'])
def api_get_reminders():
    """API - 获取提醒列表"""
    memo_id = request.args.get('memo_id', type=int)

    if memo_id:
        reminders = Reminder.get_by_memo_id(memo_id)
    else:
        # 获取待发送的提醒
        reminders = Reminder.get_pending_reminders()

    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in reminders],
        'count': len(reminders)
    })


@app.route('/api/reminders', methods=['POST'])
def api_add_reminder():
    """API - 新增提醒"""
    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    memo_id = data.get('memo_id')
    remind_at = data.get('remind_at')

    if not memo_id or not remind_at:
        return jsonify({'success': False, 'message': '备忘录ID和提醒时间不能为空'}), 400

    reminder = Reminder(
        memo_id=memo_id,
        title=data.get('title'),
        remind_at=remind_at,
        repeat_type=data.get('repeat_type', 'none'),
        repeat_end_date=data.get('repeat_end_date') or None,
        notify_channels=data.get('notify_channels', ['feishu']),
        status='pending'
    )
    reminder.save()

    return jsonify({
        'success': True,
        'message': '提醒设置成功',
        'data': reminder.to_dict()
    })


@app.route('/api/reminders/<int:reminder_id>', methods=['PUT', 'POST'])
def api_update_reminder(reminder_id):
    """API - 更新提醒"""
    reminder = Reminder.get_by_id(reminder_id)
    if not reminder:
        return jsonify({'success': False, 'message': '提醒不存在'}), 404

    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    if 'title' in data:
        reminder.title = data.get('title')
    if 'remind_at' in data:
        reminder.remind_at = data.get('remind_at')
    if 'repeat_type' in data:
        reminder.repeat_type = data.get('repeat_type')
    if 'repeat_end_date' in data:
        reminder.repeat_end_date = data.get('repeat_end_date') or None
    if 'notify_channels' in data:
        reminder.notify_channels = data.get('notify_channels')
    if 'status' in data:
        reminder.status = data.get('status')

    reminder.save()

    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': reminder.to_dict()
    })


@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
def api_delete_reminder(reminder_id):
    """API - 删除提醒"""
    if Reminder.delete_by_id(reminder_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


@app.route('/api/reminders/<int:reminder_id>/delete', methods=['GET'])
def api_delete_reminder_get(reminder_id):
    """API - 删除提醒 (GET方式)"""
    if Reminder.delete_by_id(reminder_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


@app.route('/api/reminders/<int:reminder_id>/test', methods=['POST', 'GET'])
def api_test_reminder(reminder_id):
    """API - 测试发送提醒"""
    from services.scheduler import scheduler

    reminder = Reminder.get_by_id(reminder_id)
    if not reminder:
        return jsonify({'success': False, 'message': '提醒不存在'}), 404

    # 手动触发发送
    settings = SystemSetting.get_notification_settings()

    try:
        from models.memo import Memo
        memo = Memo.get_by_id(reminder.memo_id)
        if not memo:
            return jsonify({'success': False, 'message': '关联的备忘录不存在'}), 404

        # 直接调用发送逻辑
        for channel in (reminder.notify_channels or ['feishu']):
            if channel == 'feishu':
                from services.feishu_bot import FeishuBot
                webhook_url = settings.get('feishu_webhook_url')
                if webhook_url:
                    bot = FeishuBot(webhook_url, settings.get('feishu_secret'))
                    result = bot.send_reminder(reminder, memo)
                    if not result['success']:
                        return jsonify({'success': False, 'message': f'飞书发送失败：{result["message"]}'})
                else:
                    return jsonify({'success': False, 'message': '飞书webhook未配置'})
            elif channel == 'weixin':
                from services.weixin_bot import WeixinBot
                webhook_url = settings.get('weixin_webhook_url')
                if webhook_url:
                    bot = WeixinBot(webhook_url)
                    result = bot.send_reminder(reminder, memo)
                    if not result['success']:
                        return jsonify({'success': False, 'message': f'微信发送失败：{result["message"]}'})
                else:
                    return jsonify({'success': False, 'message': '微信webhook未配置'})

        return jsonify({'success': True, 'message': '测试发送成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送失败：{str(e)}'}), 500


# ============================================
# 通知设置 API
# ============================================

@app.route('/api/settings/notifications', methods=['GET'])
def api_get_notification_settings():
    """API - 获取通知设置"""
    settings = SystemSetting.get_notification_settings()
    return jsonify({
        'success': True,
        'data': settings
    })


@app.route('/api/settings/notifications', methods=['POST', 'PUT'])
def api_save_notification_settings():
    """API - 保存通知设置"""
    data = request.get_json() or request.form
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400

    SystemSetting.save_notification_settings({
        'feishu_webhook_url': data.get('feishu_webhook_url', ''),
        'feishu_secret': data.get('feishu_secret', ''),
        'weixin_webhook_url': data.get('weixin_webhook_url', ''),
        'notification_enabled': data.get('notification_enabled', True)
    })

    return jsonify({
        'success': True,
        'message': '设置保存成功'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
