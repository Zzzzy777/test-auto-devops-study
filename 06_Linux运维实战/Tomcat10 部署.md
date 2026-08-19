# Tomcat10 部署实操文档
## 一、环境说明
- 操作系统：Ubuntu 22.04
- JDK版本：openjdk version "17.0.19"
- Tomcat版本：apache-tomcat-10.1.28
- 安装目录：/opt/tomcat10
- 默认端口：8080
- 静态IP：192.168.86.100

## 二、前置环境检查
```bash
# 检查JDK环境
java -version

# 查看是否正在运行tomcat进程
ps -ef | grep tomcat

# 查看目录是否已有tomcat文件
ls /opt
ls /usr/local
```

## 三、Tomcat 完整安装部署步骤
```bash
# 1. 切换到/opt目录
cd /opt

# 2. 下载tomcat10压缩包
sudo wget https://archive.apache.org/dist/tomcat/tomcat-10/v10.1.28/bin/apache-tomcat-10.1.28.tar.gz

# 3. 解压压缩包
sudo tar -zxvf apache-tomcat-10.1.28.tar.gz

# 4. 重命名目录简化管理
sudo mv apache-tomcat-10.1.28 tomcat10

# 5. 切换root账号，授权脚本并启动服务
sudo -i
cd /opt/tomcat10/bin
chmod +x *.sh
./startup.sh
```

## 四、外部访问配置
```bash
# 放行防火墙8080端口
sudo ufw allow 8080

# 查看本机静态IP
ip a
```
>浏览器访问地址：http://192.168.86.100:8080

## 五、Tomcat 常用运维命令
```bash
# 停止tomcat服务
./shutdown.sh

# 实时查看运行日志（排查报错）
tail -f /opt/tomcat10/logs/catalina.out
```