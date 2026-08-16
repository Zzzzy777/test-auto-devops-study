# 静态IP配置文档
## 实验环境
- 系统：Ubuntu 22.04（云镜像）
- 网卡名称：ens33
- 目标静态IP：`192.168.86.129/24`
- 网关：`192.168.86.2`
- DNS：`223.5.5.5`、`8.8.8.8`

> ⚠️重要坑：Ubuntu云镜像自带`cloud‑init`服务，如果不关闭，重启后静态IP会被自动覆盖变回dynamic动态获取。

## 操作步骤
### 1、关闭cloud‑init网络自动配置
#### 创建配置文件，禁用cloud‑init修改网络：
```bash
sudo nano /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
```

- 写入内容：network: {config: disabled}
- Ctrl+O保存，回车，Ctrl+X退出。

### 2、修改 netplan 网络配置文件
#### 编辑 netplan 配置文件
```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

#### 完整配置内容（严格注意缩进，全部使用空格，禁止使用 Tab 键）
```yaml
network:
  ethernets:
    ens33:
      addresses:
        - 192.168.86.129/24
      routes:
        - to: default
          via: 192.168.86.2
      nameservers:
        addresses: [223.5.5.5,8.8.8.8]
  version: 2
  ```
  保存退出。
  
### 3、应用网络配置
```bash
sudo netplan apply
```

### 4、验证 IP 配置
```bash
ip a
```

> ✅成功标志：ens33 没有dynamic字样，valid_lft forever，IP 为192.168.86.129。

### 5、验证外网连通
```bash
ping www.baidu.com
```

- 收到数据包代表外网正常，Ctrl+C停止 ping。

### 6、重启虚拟机做最终校验
```bash
sudo reboot
```

- 重启完成后重新连接 Xshell，再次执行ip a确认 IP 保持不变。