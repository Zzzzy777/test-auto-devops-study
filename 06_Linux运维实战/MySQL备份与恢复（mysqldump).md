# MySQL备份与恢复（mysqldump）
> 实训模块：mysqldump 数据备份、误删数据恢复演练
> 环境：Ubuntu 22.04 + MySQL 8.0
> 测试库：test_demo

## 一、前置说明
`mysqldump` 是 MySQL 官方自带的逻辑备份工具，**在 Linux 终端（bash 命令行）执行**，不要进入 mysql> 交互界面运行。
备份本质：导出为可执行的 SQL 脚本文件，恢复时直接执行该 SQL 即可还原数据。

## 二、备份实操
### 1. 整库备份（最常用）
备份 `test_demo` 整个数据库，保存为 `test_demo_backup.sql`
```bash
mysqldump -uroot -p123456 test_demo > test_demo_backup.sql
```

#### 参数说明：
1. -uroot：数据库用户名
2. -p123456：数据库密码（生产环境建议只写 -p，回车后手动输入密码，更安全）
3. test_demo：要备份的数据库名称
4. ">"：输出重定向，把备份内容写入指定文件

### 2. 单表备份
#### 只备份 user 这一张表
```bash
mysqldump -uroot -p123456 test_demo user > user_table_backup.sql
```

### 3. 只备份表结构（不备份数据）
#### 加 -d 参数，仅导出表结构定义
```bash
mysqldump -uroot -p123456 -d test_demo > test_demo_schema.sql
```

### 4. 备份所有数据库
#### 加 --all-databases 参数，备份 MySQL 实例全部数据库
```bash
mysqldump -uroot -p123456 --all-databases > all_databases_backup.sql
```

### 5. 查看备份文件
```bash
ls -lh *.sql
```

## 三、误删数据故障演练
### 进入 MySQL 命令行，模拟生产误删操作
```sql
use test_demo;

-- 模拟误删订单表
drop table orders;

-- 验证：表已消失
show tables;
```

## 四、数据恢复实操
### 1. 整库恢复（对应整库备份文件）
#### 回到 Linux 终端执行
```bash
mysql -uroot -p123456 test_demo < test_demo_backup.sql
```

#### 参数说明：
1. <：输入重定向，把 SQL 文件导入到目标数据库
2. 注意：恢复前必须确保 test_demo 数据库已存在；如果库也被删除，需要先执行 create database test_demo;

### 2. 验证恢复结果
```sql
use test_demo;
show tables;
select count(*) from user;
select count(*) from orders;
```