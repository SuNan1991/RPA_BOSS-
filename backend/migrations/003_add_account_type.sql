-- 添加账户类型字段
-- 'seeker' = 求职者, 'hr' = 招聘者
ALTER TABLE accounts ADD COLUMN account_type TEXT DEFAULT 'seeker';
