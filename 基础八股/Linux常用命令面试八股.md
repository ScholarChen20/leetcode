# Linux 常用命令面试八股

> 整理日期：2026-09-08
> 方向：后台开发 / Linux

---

## 一、性能监控

### 1. top

```bash
top          # 实时查看系统负载、CPU、内存、进程
top -H -p PID   # 查看指定进程的所有线程
```

**关键指标解读：**

```text
load average：1/5/15 分钟平均负载（CPU 核数以内正常）
%CPU：进程 CPU 使用率
%MEM：进程内存占用
RES：实际物理内存
```

**负载说明：** load average 持续大于 CPU 核数 → 系统过载。

### 2. free

```bash
free -h     # 查看内存使用情况（人类可读格式）
```

**关键指标：** `available` 才是真正可用内存，`free` 列看起来少是正常的（Linux 用空闲内存做缓存）。

### 3. df / du

```bash
df -h           # 查看磁盘分区使用情况
du -sh /path    # 查看目录总大小
du -h --max-depth=1 /path   # 查看一级子目录大小
```

### 4. iostat / vmstat

```bash
iostat -x 1    # 磁盘 IO 统计（%util 接近 100% 说明磁盘瓶颈）
vmstat 1       # 内存、CPU、上下文切换统计
```

---

## 二、网络排查

### 5. netstat / ss

```bash
netstat -tlnp    # 查看监听端口
netstat -anp | grep 8080   # 查看端口占用
ss -tlnp         # 现代替代（更快）
```

### 6. curl

```bash
curl -X POST http://localhost:8080/api -H "Content-Type: application/json" -d '{"key":"value"}'
curl -I http://example.com    # 只看响应头
curl -v http://example.com    # 详细过程
```

### 7. telnet / nc

```bash
telnet 10.0.0.1 8080    # 测试端口连通性
nc -zv 10.0.0.1 8080    # 快速端口探测
```

### 8. ping / traceroute

```bash
ping -c 4 baidu.com          # 网络连通性
traceroute baidu.com         # 路由追踪
```

---

## 三、日志与文本处理

### 9. tail / head

```bash
tail -f app.log          # 实时跟踪日志
tail -n 100 app.log      # 查看最后 100 行
head -n 20 app.log       # 查看前 20 行
```

### 10. grep

```bash
grep "ERROR" app.log                    # 查找错误
grep -n "ERROR" app.log                 # 显示行号
grep -A 5 -B 5 "ERROR" app.log          # 前后各 5 行上下文
grep -c "ERROR" app.log                 # 统计数量
grep -E "ERROR|WARN" app.log            # 正则匹配
grep "keyword" -r /path                 # 递归搜索目录
```

### 11. awk

```bash
awk '{print $1, $3}' file              # 打印第 1、3 列
awk '$3 > 100' file                    # 第三列大于 100 的行
awk '{sum += $1} END {print sum}' file # 求和
```

### 12. sed

```bash
sed -n '10,20p' file                   # 查看第 10-20 行
sed 's/old/new/g' file                 # 替换（输出不写文件）
sed -i 's/old/new/g' file              # 替换并写回
```

### 13. 组合实战

```bash
# 统计访问最多的 10 个 IP
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 统计接口耗时 TOP10
grep "cost" app.log | awk '{print $NF}' | sort -rn | head -10

# 查找大文件
find / -type f -size +100M
```

---

## 四、进程管理

### 14. ps

```bash
ps -ef              # 查看所有进程
ps -ef | grep java  # 查找 Java 进程
ps aux --sort=-%cpu # 按 CPU 排序
```

### 15. kill

```bash
kill PID            # 优雅终止（SIGTERM）
kill -9 PID         # 强制终止（SIGKILL）
kill -15 PID        # 默认信号
pkill -f "pattern"  # 按名称模式杀进程
```

### 16. 后台进程

```bash
nohup java -jar app.jar > app.log 2>&1 &   # 后台运行，不随终端退出
jobs                # 查看后台任务
fg %1               # 前台恢复
```

---

## 五、文件操作

### 17. 查找文件

```bash
find /path -name "*.log"              # 按名称查找
find /path -type f -mtime -1          # 最近 1 天修改的文件
find /path -name "*.tmp" -delete      # 查找并删除
```

### 18. 压缩解压

```bash
tar -czf archive.tar.gz /path         # 压缩
tar -xzf archive.tar.gz               # 解压
tar -xzf archive.tar.gz -C /target    # 解压到指定目录
zip -r file.zip /path                 # zip 压缩
unzip file.zip                        # zip 解压
```

### 19. 权限

```bash
chmod 755 file                        # rwxr-xr-x
chmod -R 755 /path                    # 递归修改
chown user:group file                 # 修改属主
```

### 20. 传输

```bash
scp file user@host:/path              # 复制到远程
scp user@host:/path/file ./           # 从远程复制
```

---

## 六、JVM 相关（Java 场景常用）

```bash
jps                  # 查看 Java 进程
jstack PID           # 线程堆栈（死锁、CPU 高排查）
jmap -heap PID       # 堆内存信息
jmap -dump:format=b,file=heap.hprof PID   # 堆转储
jstat -gcutil PID 1000   # GC 统计每秒刷新
```

**经典排查流程：**

```bash
# CPU 飙高定位
top                      # 找到高 CPU 进程 PID
top -Hp PID              # 找到高 CPU 线程 TID
printf '%x\n' TID        # 转十六进制
jstack PID | grep -A 20 十六进制TID   # 定位代码
```

---

## 七、高频追问

| 追问 | 答案要点 |
|---|---|
| 怎么查端口被谁占用 | `netstat -tlnp` 或 `ss -tlnp` 或 `lsof -i:端口` |
| load average 多少算高 | 持续大于 CPU 核数 |
| 大日志怎么找错误 | `grep "ERROR"` + `tail` 配合，必要时分片处理 |
| 杀不掉的进程怎么办 | 先 `kill -15`，无效再 `kill -9`，检查是否 D 状态（IO 阻塞） |
| 如何实时看日志 | `tail -f` |
| 磁盘满怎么排查 | `df -h` 定位分区 → `du -h --max-depth=1` 逐层定位 |
