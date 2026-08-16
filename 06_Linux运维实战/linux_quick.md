# Linux高频命令速查表（测试方向）
> 用途：运维、接口自动化排查日志、进程、端口

## 1.目录与文件操作
|命令|说明|
|---|---|
|`pwd`|查看当前路径|
|`ls -la`|列出全部文件包含隐藏文件|
|`cd xxx`|进入目录；`cd ..` 返回上级目录|
|`mkdir xxx`|创建文件夹|
|`touch file.txt`|新建空文件|
|`cp src dst`|复制文件|
|`mv old new`|移动/重命名|
|`rm -rf folder`|强制删除文件夹，⚠️慎用|
|`cat file`|查看全部文件|
|`tail -f log.txt`|**实时查看日志，测试最常用**|

## 2.搜索命令
|命令|说明|
|---|---|
|`grep "关键词" log.txt`|文件内搜索关键字|
|`grep -i "err" log.txt`|忽略大小写搜索|
|`find ./ -name "*.log"`|查找目录下log文件|

## 3.进程操作
|命令|说明|
|---|---|
|`ps -ef`|查看全部进程|
|`ps -ef \| grep python`|过滤查找python进程|
|`kill 1234`|关闭进程|
|`kill -9 1234`|强制杀死进程|

## 4.端口排查（接口测试重点）
|命令|说明|
|---|---|
|`netstat -tulpn \| grep 8080`|查看8080端口被哪个程序占用|
|`ss -tulpn \| grep 8080`|新版系统查看端口|

## 5.压缩解压
|命令|说明|
|---|---|
|`tar -zcvf out.tar.gz folder`|压缩|
|`tar -zxvf out.tar.gz`|解压|

## 6.权限
|命令|说明|
|---|---|
|`chmod +x run.sh`|给脚本添加可执行权限|

## 7.管道符号 `|`
把前面命令输出交给后面命令处理
```bash
ps -ef | grep python
cat run.log | grep fail
```

## 8.重点记忆：
1. `tail -f`：看程序日志，定位接口报错
2.  `ps | grep`：看程序有没有跑起来
3. `netstat`：看服务端口有没有监听成功



## 9.具体运用示例
### 一、基础文件目录命令
```bash
# 查看当前所在路径
pwd

# 列出目录内容
ls          # 列出文件
ls -l       # 详细信息
ls -la      # 包含隐藏文件

# 切换目录
cd /home
cd ..       # 返回上一级
cd ~        # 回到家目录

# 创建文件夹
mkdir test_demo

# 创建文件
touch log.txt

# 复制
cp log.txt ./test_demo/

# 移动/重命名
mv log.txt new_log.txt

# 删除
rm file.txt         # 删除文件
rm -rf test_demo    # 删除文件夹（⚠️谨慎使用）

# 查看文件内容
cat log.txt
more log.txt
tail -f log.txt     # 实时滚动看日志，测试排查日志超级常用
```

### 二、搜索命令
```bash
# 文件中搜索关键字
grep "error" log.txt
grep -i "error" log.txt   # -i忽略大小写

# 查找磁盘上的文件
find ./ -name "*.log"     # 当前目录下找所有log后缀文件
```

### 三、进程相关命令
```bash
ps -ef                    # 查看全部进程
ps -ef | grep python      # 过滤查找python进程

# 杀死进程
kill 进程号
kill -9 进程号             # 强制杀掉进程
```

### 四、端口查看命令（接口测试重点！排查服务有没有启动）
```bash
# 查看端口占用，看哪个程序占用8080端口
netstat -tulpn | grep 8080

# 部分系统用ss替代netstat
ss -tulpn | grep 8080
```

### 五、压缩解压
```bash
# 压缩
tar -zcvf demo.tar.gz demo_folder
# 解压
tar -zxvf demo.tar.gz
```

### 六、权限命令
```bash
# 修改文件权限
chmod 755 test.txt

# 修改文件所属用户
chown ubuntu:ubuntu test.txt

# -R 递归，对文件夹内部全部文件生效
chmod -R 777 mydir
chown -R ubuntu:ubuntu mydir
```

### 七、管道 | 非常重要

> 把上一个命令输出交给下一个命令处理
```bash
ps -ef | grep python
cat log.txt | grep fail
```