# 8.24 Shell 基础语法
> 学习目标：掌握变量、if 判断、for 循环；能看懂并编写短小实用脚本
> 实战产出：简单端口检测脚本

## 1. Shell 脚本入门
Shell 脚本：将多条 Linux 命令按顺序写入 `.sh` 文件，批量自动执行。

### 第一个脚本运行三步法
```bash
# 1. 创建文件
touch first.sh

# 2. 编辑内容（首行固定声明解释器）
#!/bin/bash
echo "hello shell"

# 3. 添加执行权限并运行
chmod +x first.sh
./first.sh