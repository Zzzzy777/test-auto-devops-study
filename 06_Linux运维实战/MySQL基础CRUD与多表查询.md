# MySQL基础CRUD与多表查询 实训笔记
> 实训模块：MySQL库、表创建、数据增删改查、分组聚合、多表连接查询
> 适配岗位：自动化测试 / Linux运维

## 一、数据库基础操作
### 1. 创建数据库
```sql
create database test_demo;
```

### 2. 查看所有数据库
```sql
show databases;
```

### 3. 使用（切换）数据库
```sql
use test_demo;
```

### 4. 删除数据库
```sql
drop database if exists test_demo;
```
>⚠警告：删除数据库，库内所有表和数据全部清除，谨慎操作

## 二、创建数据表
### 1. 创建 user 用户表
```sql
CREATE TABLE user(
id INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(32),
age INT,
phone VARCHAR(11),
email VARCHAR(50),
create_time DATETIME
);
```

### 2. 创建 orders 订单表（避开 order 关键字，不用反引号）
```sql
CREATE TABLE orders(
id INT PRIMARY KEY AUTO_INCREMENT,
order_no VARCHAR(32),
user_id INT,
create_time DATETIME
);
```

### 3. 查看当前库下所有表
```sql
show tables;
```

### 4. 查看表结构
```sql
desc user;
desc orders;
```

### 5. 删除数据表
```sql
-- 删除单张表
drop table orders;

-- 一次性删除多张表，逗号分隔
drop table if exists user,orders;
```
>⚠高危提醒：drop table 删除【表结构 + 全部数据】，删除后无法恢复

### 三种清空表数据对比
| 命令 | 删除内容 | 表结构是否保留 | 是否可回滚 |
| ---- | -------- | -------------- | ---------- |
| delete | 表内数据 | ✅保留 | ✅支持事务回滚 |
| truncate | 全部数据 | ✅保留 | ❌不可回滚 |
| drop table | 数据 + 表结构 | ❌删除 | ❌不可回滚 |

## 三、基础 CRUD（Create 新增 Read 查询 Update 修改 Delete 删除）
### 1. INSERT 新增数据
- 使用场景：向数据表插入全新记录（造测试数据、业务新增数据）
```sql
-- 单行插入
insert into user(username,age,phone) values ('zhangsan',22,'13800138000');

-- 多行批量插入
insert into orders(order_no,user_id,create_time)
values
('ORD20260819001',1,now()),
('ORD20260819002',2,now());
```
>注意：字符串使用单引号包裹；自增主键 id 可省略，数据库自动生成

### 2. SELECT 查询数据
```sql
-- 查询指定字段（推荐，不要直接select *）
select id,username,age from user;

-- 多条件查询 and / or
select * from user where age>20 and username='zhangsan';

-- 模糊查询 % 匹配任意字符
select * from user where username like 'test_user%';

-- 排序：asc升序（默认），desc降序
select * from user order by id desc;

-- 分页 limit 起始下标,条数
select * from user limit 0,10;

-- 聚合函数 count sum avg max min
select count(*) from user;
select avg(age),max(age),min(age) from user;
```

### 3. UPDATE 修改已有数据
- 使用场景：修改数据库中已经存在的记录
```sql
-- 修改指定id数据（必须加where条件！）
update user set email = 'zhangsan@qq.com' where id = 1;
```
>⚠高危警告：不加 where，会修改整张表全部数据！
>规范：update 执行前，先用 select 确认筛选范围

### 4. DELETE 删除数据
- 使用场景：删除表中已存在的行记录
```sql
-- 删除符合条件数据
delete from user where id > 100;
delete from user where username='wangwu';
```
>⚠高危警告：delete from user; 不带 where 会清空全表数据

## 四、分组聚合 group by + having
>MySQL5.7 及以上默认开启 only_full_group_by 严格模式
>规则：select 后普通字段，必须出现在 group by 中，否则报错
```sql
-- 按年龄分组，统计每个年龄人数
select age,count(*) from user group by age;

-- having 过滤分组后的结果（where过滤原始数据，分组后用having）
select age,count(*) from user group by age having count(*)>1;
```
>面试考点：where 在分组前过滤原始数据；having 在分组完成后过滤聚合结果

## 五、表结构操作 alter
```sql
-- 新增字段
alter table user add column email varchar(50);

-- 修改字段类型
alter table user modify column email varchar(100);

-- 删除字段
alter table user drop column email;
```

## 六、多表连接查询（自动化测试高频考点）
### 1. inner join 内连接（重点掌握）
>含义：只查询两张表匹配成功的数据
```sql
select u.username,o.order_no
from user u
inner join orders o
on u.id = o.user_id;
```

### 2. left join 左连接
>含义：左侧表全部数据保留，右表匹配不到数据显示 null
```sql
select u.username,o.order_no
from user u
left join orders o
on u.id = o.user_id;
```
