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

---

## 八、Docker 面试基础

### 21. Docker 和虚拟机有什么区别？

**参考答案：** Docker 容器共享宿主机内核，属于进程级隔离，启动快、资源占用少；虚拟机运行完整操作系统，隔离性更强但开销更大。

### 22. Docker 的核心概念有哪些？

- 镜像：容器运行所需的只读模板；
- 容器：镜像运行后的实例；
- 仓库：存储和分发镜像；
- Docker Engine：负责构建、运行和管理容器。

关系：Dockerfile → Image → Container。

### 23. Dockerfile 常用指令有哪些？

FROM 表示基础镜像，RUN 在构建时执行命令，COPY 复制文件，WORKDIR 设置工作目录，ENV 设置环境变量，EXPOSE 声明端口，CMD 和 ENTRYPOINT 定义启动命令。

### 24. CMD 和 ENTRYPOINT 有什么区别？

CMD 是默认启动命令，可以被运行参数覆盖；ENTRYPOINT 是固定入口，通常用于定义容器必须执行的主程序。二者可以组合使用。

### 25. Docker 容器为什么会退出？

常见原因是主进程执行结束、启动命令错误、配置缺失、依赖服务不可用或应用启动后崩溃。

排查命令：

    docker ps -a
    docker logs <container>
    docker inspect <container>
    docker exec -it <container> sh

### 26. Docker 如何持久化数据？

容器删除后容器层数据可能丢失，应使用 Volume 或宿主机目录挂载。

    docker run -v /host/data:/app/data image

常用于数据库文件、配置文件和日志持久化。

### 27. Docker 不同网络模式有什么区别？

**参考答案：**

| 网络模式 | 网络特点 | 典型应用 |
|---|---|---|
| bridge | 默认模式，容器拥有独立网络命名空间，通过虚拟网桥和 NAT 访问外部；同一自定义网络中的容器可通过名称通信 | 普通 Web 应用、MySQL、Redis 等单机容器部署 |
| host | 容器直接使用宿主机网络，不再拥有独立 IP，网络性能好但隔离性弱 | 对网络性能要求高，或需要直接监听宿主机端口的服务 |
| none | 不配置网络，容器只有本地回环接口 | 安全隔离、只执行本地计算的任务 |
| container | 与指定容器共享网络命名空间，共享 IP 和端口 | Sidecar、调试或需要共享网络的容器 |
| overlay | 跨 Docker 主机建立虚拟网络，容器可以跨节点通信 | Docker Swarm 等多主机容器编排 |
| macvlan | 为容器分配独立 MAC 和局域网 IP，使容器像物理主机一样接入局域网 | 需要被局域网设备直接访问的传统应用 |

### 28. bridge 和 host 模式如何选择？

- 需要网络隔离、容器独立 IP 和服务间通信：选择 bridge 或自定义 bridge；
- 追求网络性能、减少 NAT 开销：可以选择 host，但要注意端口冲突和隔离性下降；
- 普通业务容器通常优先使用自定义 bridge，而不是直接使用默认 bridge。

### 29. Docker 自定义网络有什么好处？

- 容器可以通过服务名或容器名互相访问，不依赖固定 IP；
- 可以按业务划分网络，减少无关容器之间的通信；
- 支持更清晰的服务隔离和网络管理；
- Docker Compose 默认会为同一项目创建自定义网络。

### 30. Docker 网络模式面试总结

> 单机普通业务使用 bridge；高性能或需要直接使用宿主机端口时使用 host；完全隔离网络使用 none；跨主机容器通信使用 overlay；需要容器直接接入物理局域网时使用 macvlan。

### 31. Docker Compose 有什么作用？

Compose 使用 YAML 文件描述多个容器及其依赖，适合本地或单机环境编排，例如应用、MySQL、Redis 和 Nginx 一起启动。

### 32. Docker 如何减小镜像体积？

使用精简基础镜像、多阶段构建、.dockerignore，只复制运行所需文件，并清理构建缓存。

### 33. Docker 常用命令有哪些？

    docker pull image
    docker build -t app:v1 .
    docker run -d --name app image
    docker ps -a
    docker logs -f app
    docker exec -it app sh
    docker stop app
    docker rm app

---

## 九、Kubernetes 面试基础

### 31. Kubernetes 解决什么问题？

**参考答案：** Kubernetes 是容器编排平台，负责容器的自动部署、调度、扩缩容、服务发现、负载均衡和故障自愈。

简单理解：Docker 负责运行容器，Kubernetes 负责管理大量容器。

### 32. Kubernetes 的核心组件有哪些？

控制面：API Server 统一入口，Scheduler 负责调度，Controller Manager 维护期望状态，etcd 保存集群状态。

工作节点：kubelet 管理 Pod，kube-proxy 维护网络规则，容器运行时负责启动容器。

### 33. Pod 是什么？

Pod 是 Kubernetes 最小的部署和调度单位，通常包含一个容器，也可以包含多个需要共享网络和存储的容器。

同一 Pod 中的容器共享网络命名空间，可以通过 localhost 通信，也可以共享 Volume。

### 34. Deployment 有什么作用？

Deployment 用于管理无状态应用，提供副本数管理、滚动更新、版本回滚、故障重建和扩缩容。

关系：Deployment → ReplicaSet → Pod。

### 35. Service 有什么作用？

Service 为一组 Pod 提供稳定的访问入口和负载均衡。因为 Pod 会动态创建和销毁，Service 用标签选择器找到 Pod，并提供稳定的虚拟 IP 和 DNS 名称。

常见类型：ClusterIP、NodePort、LoadBalancer。

### 36. Ingress 有什么作用？

Ingress 根据域名或路径把外部 HTTP/HTTPS 请求转发到不同 Service，通常需要配合 Ingress Controller 使用。

### 37. ConfigMap 和 Secret 有什么区别？

ConfigMap 保存普通配置；Secret 保存密码、Token 和证书等敏感信息。二者都可以通过环境变量或 Volume 注入 Pod。

Secret 默认只是编码存储，不等于绝对安全，还需要配合权限控制和密钥管理。

### 38. Kubernetes 如何实现服务发现？

Service 提供稳定的虚拟 IP 和 DNS 名称，集群内 Pod 可以通过 Service 名称访问目标服务，通常由 CoreDNS 提供解析。

### 39. livenessProbe 和 readinessProbe 有什么区别？

- livenessProbe：判断应用是否还活着，失败后重启容器；
- readinessProbe：判断应用是否可以接收流量，失败后从 Service 摘除 Pod。

面试口诀：liveness 决定是否重启，readiness 决定是否接流量。

### 40. Kubernetes 如何实现滚动更新？

Deployment 逐步创建新版本 Pod，同时逐步减少旧版本 Pod，从而实现服务基本不中断的更新；更新失败可以回滚。

    kubectl rollout status deployment/app
    kubectl rollout undo deployment/app

### 41. requests 和 limits 有什么区别？

requests 是调度时申请的资源，决定 Pod 是否能放到某个节点；limits 是容器可使用的资源上限。

CPU 超限通常会被限制，内存超限可能导致 OOMKilled。

### 42. Pod 一直 Pending 怎么排查？

常见原因：节点资源不足、requests 过大、节点污点或亲和性不满足、PVC 异常。

    kubectl describe pod <pod>
    kubectl get nodes
    kubectl get events

### 43. Pod 出现 CrashLoopBackOff 怎么排查？

表示容器反复启动失败并进入退避重启。重点检查应用日志、环境变量、配置文件、依赖服务、探针、OOM 和权限。

    kubectl logs <pod>
    kubectl logs <pod> --previous
    kubectl describe pod <pod>

### 44. Docker 和 Kubernetes 如何配合？

    Dockerfile → 构建镜像 → 推送镜像仓库
                                      ↓
    Kubernetes Deployment → 创建 Pod → Service / Ingress 对外提供访问

Docker 负责镜像构建和容器运行，Kubernetes 负责多节点容器编排和服务治理。

---

## 十、Docker 与 Kubernetes 高频速记

| 问题 | 直接回答 |
|---|---|
| Docker 和虚拟机区别 | Docker 共享宿主机内核，虚拟机运行完整操作系统 |
| 镜像和容器区别 | 镜像是模板，容器是运行实例 |
| 容器为什么退出 | 主进程结束或应用启动失败 |
| Docker 数据如何持久化 | 使用 Volume 或目录挂载 |
| Kubernetes 最小调度单位 | Pod |
| Deployment 的作用 | 管理 Pod 副本、滚动更新和回滚 |
| Service 的作用 | 提供稳定访问入口和负载均衡 |
| Ingress 的作用 | 根据域名或路径转发请求 |
| liveness 和 readiness | 前者决定是否重启，后者决定是否接流量 |
| requests 和 limits | 前者用于调度，后者限制资源上限 |
| Pod Pending 怎么查 | describe Pod、查看节点资源和 events |
| CrashLoopBackOff 怎么查 | logs、previous logs、describe Pod |