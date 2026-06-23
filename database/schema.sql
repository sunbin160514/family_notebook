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
