---
name: family-notebook-manager
description: "家庭管理系统 - 管理家人信息、备忘录、定时提醒，支持飞书/微信推送通知"
---

# 家庭管理系统

完整的家庭管理解决方案，包括家人信息管理、备忘录记录、定时提醒等功能，支持通过飞书/微信推送消息。

API基础URL: http://127.0.0.1:5000

---

## 家人管理

### 查询家人

查询所有家人:
```bash
curl -s http://127.0.0.1:5000/api/members
```

按姓名搜索:
```bash
curl -s "http://127.0.0.1:5000/api/members?search=张三"
```

### 添加家人

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"李四","favorite_foods":"火锅","favorite_sports":"篮球"}' \
  http://127.0.0.1:5000/api/members
```

### 更新家人信息

先搜索获取ID，然后更新:
```bash
# 1. 搜索获取ID
curl -s "http://127.0.0.1:5000/api/members?search=张三"

# 2. 更新指定字段 (ID替换为实际值)
curl -s "http://127.0.0.1:5000/api/members/1/update?favorite_foods=火锅"
```

### 删除家人

```bash
curl -s http://127.0.0.1:5000/api/members/1/delete
```

---

## 备忘录管理

### 查询备忘录

查询所有备忘录:
```bash
curl -s http://127.0.0.1:5000/api/memos
```

按分类筛选:
```bash
curl -s "http://127.0.0.1:5000/api/memos?category=medical"
```

按关联家人筛选:
```bash
curl -s "http://127.0.0.1:5000/api/memos?member_id=1"
```

搜索备忘录:
```bash
curl -s "http://127.0.0.1:5000/api/memos?search=医院"
```

### 添加备忘录

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"title":"张三下周三医院复查","content":"记得带上医保卡和检查报告","family_member_id":1,"category":"medical","priority":"high"}' \
  http://127.0.0.1:5000/api/memos
```

分类选项：life(生活)、medical(医疗)、education(教育)、work(工作)、other(其他)
优先级：low(低)、normal(中)、high(高)

### 更新备忘录

```bash
curl -s -X PUT -H "Content-Type: application/json" \
  -d '{"title":"更新后的标题","content":"更新后的内容"}' \
  http://127.0.0.1:5000/api/memos/1
```

### 删除备忘录

```bash
curl -s http://127.0.0.1:5000/api/memos/1/delete
```

---

## 提醒管理

### 查询提醒

查询所有提醒:
```bash
curl -s http://127.0.0.1:5000/api/reminders
```

查询某个备忘录的提醒:
```bash
curl -s "http://127.0.0.1:5000/api/reminders?memo_id=1"
```

### 添加提醒

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"memo_id":1,"title":"复查提醒","remind_at":"2024-07-10 09:00:00","repeat_type":"none","notify_channels":["feishu","weixin"]}' \
  http://127.0.0.1:5000/api/reminders
```

重复类型：none(不重复)、daily(每天)、weekly(每周)、monthly(每月)、yearly(每年)
通知渠道：["feishu"]、["weixin"]或["feishu","weixin"]

### 删除提醒

```bash
curl -s http://127.0.0.1:5000/api/reminders/1/delete
```

### 测试发送提醒

```bash
curl -s -X POST http://127.0.0.1:5000/api/reminders/1/test
```

---

## 通知设置

### 获取当前设置

```bash
curl -s http://127.0.0.1:5000/api/settings/notifications
```

### 保存通知设置

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"feishu_webhook_url":"https://open.feishu.cn/...","weixin_webhook_url":"https://qyapi.weixin.qq.com/...","notification_enabled":true}' \
  http://127.0.0.1:5000/api/settings/notifications
```

---

## 典型使用场景

### 场景1：记录备忘录并设置提醒

用户说："记录备忘录：张三下周三要去医院复查，设置提醒明天早上9点"

操作步骤：
1. 先查询张三的ID：
   ```bash
   curl -s "http://127.0.0.1:5000/api/members?search=%E5%BC%A0%E4%B8%89"
   ```

2. 创建备忘录：
   ```bash
   curl -s -X POST -H "Content-Type: application/json" \
     -d '{"title":"张三下周三医院复查","content":"记得带上医保卡和检查报告","family_member_id":1,"category":"medical","priority":"high"}' \
     http://127.0.0.1:5000/api/memos
   ```

3. 获取返回的memo_id，设置提醒：
   ```bash
   curl -s -X POST -H "Content-Type: application/json" \
     -d '{"memo_id":1,"title":"医院复查提醒","remind_at":"2024-07-09 09:00:00","notify_channels":["feishu"]}' \
     http://127.0.0.1:5000/api/reminders
   ```

### 场景2：查询今天的待办事项

用户说："查看今天有什么提醒"

```bash
curl -s http://127.0.0.1:5000/api/reminders
# 筛选今天待发送的提醒
```

### 场景3：快速记录临时备忘录

用户说："记一下：家里的牙膏快用完了"

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"title":"买牙膏","content":"家里的牙膏快用完了","category":"life","priority":"normal"}' \
  http://127.0.0.1:5000/api/memos
```

---

## 数据字段说明

### 家人字段
- name: 姓名（必填）
- nickname: 昵称
- solar_birthday: 阳历生日 (YYYY-MM-DD)
- lunar_birthday: 阴历生日
- favorite_foods: 喜欢的食物
- favorite_sports: 喜欢的运动
- disliked_foods: 讨厌的食物
- daily_notes: 日常注意事项
- remarks: 备注

### 备忘录字段
- title: 标题（必填）
- content: 内容
- family_member_id: 关联家人ID（可选）
- category: 分类 (life/medical/education/work/other)
- priority: 优先级 (low/normal/high)
- status: 状态 (active/archived/deleted)

### 提醒字段
- memo_id: 关联备忘录ID（必填）
- title: 提醒标题
- remind_at: 提醒时间 (YYYY-MM-DD HH:MM:SS)
- repeat_type: 重复类型 (none/daily/weekly/monthly/yearly)
- repeat_end_date: 重复结束日期
- notify_channels: 通知渠道 ["feishu"]/["weixin"]/["feishu","weixin"]
- status: 状态 (pending/sent/read/failed)

---

## 处理流程

1. 识别用户意图（家人管理/备忘录/提醒/设置）
2. 提取关键信息（姓名、标题、时间、内容等）
3. 按顺序调用API：
   - 如需关联家人 → 先搜索家人获取ID
   - 如需设置提醒 → 先创建备忘录获取ID → 再创建提醒
4. 解析JSON响应
5. 向用户展示结果
6. 中文参数需要URL编码

---

## Web界面

- 家人管理：http://127.0.0.1:5000/
- 备忘录：http://127.0.0.1:5000/memos
- 通知设置：http://127.0.0.1:5000/settings/notifications
