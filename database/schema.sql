-- 创建数据库
CREATE DATABASE IF NOT EXISTS family_notebook DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE family_notebook;

-- 家人信息表
CREATE TABLE IF NOT EXISTS family_members (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    solar_birthday DATE DEFAULT NULL COMMENT '阳历生日',
    lunar_birthday VARCHAR(20) DEFAULT NULL COMMENT '阴历生日',
    favorite_foods TEXT COMMENT '喜欢的食物',
    favorite_sports TEXT COMMENT '喜欢的运动',
    disliked_foods TEXT COMMENT '讨厌的食物',
    daily_notes TEXT COMMENT '日常注意事项',
    remarks TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='家人信息表';

-- 插入示例数据
INSERT INTO family_members (name, nickname, solar_birthday, lunar_birthday, favorite_foods, favorite_sports, disliked_foods, daily_notes, remarks) VALUES
('张三', '阿三', '1990-05-15', '四月初一', '红烧肉、清蒸鱼、草莓', '篮球、游泳', '苦瓜、香菜', '血压偏高，少吃盐', '爸爸'),
('李四', '小四', '1992-08-20', '七月廿三', '火锅、奶茶、巧克力', '瑜伽、跑步', '洋葱、蒜', '乳糖不耐受', '妈妈');

-- ============================================
-- 备忘录模块 (新增)
-- ============================================

-- 备忘录表
CREATE TABLE IF NOT EXISTS memos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT COMMENT '内容',
    family_member_id INT DEFAULT NULL COMMENT '关联家人ID，可为空',
    category ENUM('life', 'medical', 'education', 'work', 'other') DEFAULT 'life' COMMENT '分类：生活、医疗、教育、工作、其他',
    priority ENUM('low', 'normal', 'high') DEFAULT 'normal' COMMENT '优先级：低、中、高',
    status ENUM('active', 'archived', 'deleted') DEFAULT 'active' COMMENT '状态：活跃、归档、删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (family_member_id) REFERENCES family_members(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备忘录表';

-- 提醒表
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    memo_id INT NOT NULL COMMENT '关联备忘录ID',
    title VARCHAR(200) COMMENT '提醒标题',
    remind_at DATETIME NOT NULL COMMENT '提醒时间',
    repeat_type ENUM('none', 'daily', 'weekly', 'monthly', 'yearly') DEFAULT 'none' COMMENT '重复类型：无、每天、每周、每月、每年',
    repeat_end_date DATE DEFAULT NULL COMMENT '重复结束日期',
    notify_channels JSON COMMENT '通知渠道：["feishu", "weixin"]',
    status ENUM('pending', 'sent', 'read', 'failed') DEFAULT 'pending' COMMENT '状态：待发送、已发送、已读、失败',
    last_sent_at TIMESTAMP NULL COMMENT '最后发送时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (memo_id) REFERENCES memos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提醒表';

-- 通知日志表
CREATE TABLE IF NOT EXISTS notification_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    reminder_id INT NOT NULL COMMENT '关联提醒ID',
    channel VARCHAR(20) COMMENT '通知渠道：feishu/weixin',
    status VARCHAR(20) COMMENT '发送状态：success/failed',
    response TEXT COMMENT '接口返回内容',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知日志表';

-- 系统设置表（存储飞书/微信配置）
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE COMMENT '设置键',
    setting_value TEXT COMMENT '设置值',
    description VARCHAR(255) COMMENT '说明',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统设置表';
