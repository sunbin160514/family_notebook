from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import sys

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.family_member import FamilyMember
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY


@app.route('/')
def index():
    """首页 - 显示家人列表和搜索"""
    search = request.args.get('search', '').strip()
    members = FamilyMember.get_all(search=search if search else None)
    birthday_reminders = FamilyMember.get_birthday_reminders(days=7)

    return render_template('index.html',
                         members=[m.to_dict() for m in members],
                         birthday_reminders=birthday_reminders,
                         search=search)


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    """添加家人"""
    if request.method == 'POST':
        data = request.form
        member = FamilyMember(
            name=data.get('name'),
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
        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/members/<int:member_id>')
def member_detail(member_id):
    """查看家人详情"""
    member = FamilyMember.get_by_id(member_id)
    if not member:
        return redirect(url_for('index'))
    return render_template('detail.html', member=member.to_dict())


@app.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
def edit_member(member_id):
    """编辑家人信息"""
    member = FamilyMember.get_by_id(member_id)
    if not member:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.form
        member.name = data.get('name')
        member.nickname = data.get('nickname')
        member.solar_birthday = data.get('solar_birthday') or None
        member.lunar_birthday = data.get('lunar_birthday')
        member.favorite_foods = data.get('favorite_foods')
        member.favorite_sports = data.get('favorite_sports')
        member.disliked_foods = data.get('disliked_foods')
        member.daily_notes = data.get('daily_notes')
        member.remarks = data.get('remarks')
        member.save()
        return redirect(url_for('index'))

    return render_template('edit.html', member=member.to_dict())


@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """删除家人"""
    if FamilyMember.delete_by_id(member_id):
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'message': '删除失败'}), 400


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
