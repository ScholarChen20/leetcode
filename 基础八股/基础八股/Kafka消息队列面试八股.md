# 消息队列中间件（Kafka）面试八股

> 整理日期：2026-09-08
> 方向：后台开发 / 消息中间件 / Kafka 核心原理

---

## Q1. Kafka 是什么？核心原理

**定位：** 分布式、分区、多副本的发布订阅消息系统，特点是高吞吐、持久化、可扩展。

**核心组成：**

```text
Producer（生产者）
  ↓ 发送
Broker（代理节点，Kafka 服务实例）
  ↓ 存储
Topic（主题，逻辑上的消息分类）
  ├─ Partition（分区，物理存储单元，可并行）
  └─ Replica（副本，主从复制）
  ↓ 消费
Consumer（消费者）+ Consumer Group（消费者组）
```

**核心原理：**

1. **顺序写盘**：消息按顺序追加到日志文件，磁盘顺序写性能接近内存
2. **页缓存（Page Cache）**：读写优先走 OS 页缓存，零拷贝技术（sendfile）直接发送
3. **分区并行**：Topic 按分区分布到不同 Broker，生产消费都能并行
4. **日志分段**：`Log` → `LogSegment`（`.log` + `.index` + `.timeindex`），按大小或时间滚动
5. **索引机制**：稀疏索引，通过 offset 定位消息位置

---

## Q2. 为什么 Kafka 吞吐量高？

```text
1. 顺序写盘 + 页缓存，写入接近内存速度
2. 零拷贝（sendfile），减少内核态和用户态之间的数据复制
3. 批量发送（batch.size）、批量压缩（压缩率比单条高）
4. 分区并行，多个消费者同时消费不同分区
5. Consumer 拉取模式（pull），按自身能力消费，天然削峰
6. 消息可累积在磁盘，不需要实时推给所有消费者
```

---

## Q3. 分区（Partition）机制

### 为什么分区

- 一个分区只能被消费者组内的一个消费者消费
- 分区数决定并行度上限，是水平扩展的关键

### 分区规则

```text
有 key：hash(key) % 分区数
无 key：轮询或随机（不同版本策略不同）
```

**注意：** 指定 key 后，相同 key 的消息一定进入同一分区，保证同一 key 的有序性。

### 分区数量的选择

```text
考虑因素：
- 吞吐需求：分区越多并行度越高
- 消费者数量：分区数要 >= 消费者数，否则部分消费者空闲
- 文件句柄限制：每个分区占多个文件句柄
- 分区不能随意缩减，扩容需评估再平衡成本
```

### 分区带来的问题

- Kafka 只能保证**分区内有序**，跨分区无法保证全局有序
- 需要全局有序时：单分区，或者业务层做排序合并

---

## Q4. 副本（Replica）机制

### 基本概念

```text
Leader Replica：处理所有读写请求
Follower Replica：从 Leader 同步数据，Leader 挂掉后可接任
ISR（In-Sync Replicas）：与 Leader 保持同步的副本集合
```

### 复制流程

```text
Producer → Leader 写日志
        → Follower 拉取（Fetch）同步
        → 同步进度满足条件则保留在 ISR 中
```

### ISR 与副本同步

```text
落后条件：
- Follower 落后时间超过 replica.lag.time.max.ms（默认 10s）
- 或落后消息数量超过阈值

满足条件即从 ISR 中剔除
```

### 副本相关可靠性配置

| 配置 | 含义 |
|---|---|
| `acks=0` | 不等待确认，可能丢消息 |
| `acks=1` | Leader 落盘即确认，Leader 挂可能丢 |
| `acks=all/-1` | 所有 ISR 副本确认，可靠性最高 |
| `min.insync.replicas` | 最小同步副本数，配合 `acks=all` 使用 |

**推荐组合：**

```text
acks=all + min.insync.replicas=2 + replication.factor=3
```

> 常见误解：`acks=all` 不是等所有副本，而是等 ISR 中的所有副本确认。如果 ISR 只剩 Leader 一个，`acks=all` 也退化成 `acks=1`。

### 副本相关的读写一致性问题

- Kafka 保证：**已确认的消息在 Leader 切换后不丢失**
- Follower 可能有短暂滞后，但不会返回给消费者未确认的消息

---

## Q5. 消费者组（Consumer Group）机制

### 核心规则

```text
1. 同一消费者组内的消费者共同消费一个 Topic
2. 一个分区只能被组内一个消费者消费
3. 组内消费者数量超过分区数时，多余消费者空闲
4. 不同消费者组互相独立，各自消费全量消息
```

### 消费模型

```text
主题有 6 个分区，组 A 有 3 个消费者：
消费者 1 → 分区 0、1
消费者 2 → 分区 2、3
消费者 3 → 分区 4、5
```

### Rebalance（再平衡）

```text
触发时机：
- 消费者加入或离开组
- Topic 分区数变化
- 消费者长时间未发送心跳（session.timeout.ms）

过程：
所有消费者暂停消费 → 重新分配分区 → 恢复消费
```

**Rebalance 的影响：** 期间消费者停止消费，可能导致消息堆积和重复消费，需关注。

### 提交偏移量（Offset）

```text
自动提交（enable.auto.commit=true）
- 优点：简单
- 缺点：可能重复消费或丢失消息

手动提交（enable.auto.commit=false）
- 同步提交 commitSync：可靠，阻塞
- 异步提交 commitAsync：不阻塞，需处理回调
```

---

## Q6. 消息可靠性保障

### 生产者不丢消息

```text
配置建议：
- acks=all
- retries=3（或更大）
- 开启幂等（enable.idempotence=true）
- 事务（需要 Exactly-Once 时）
- 设置合适的分区和批量发送配置
```

**重试注意：** 开启重试后可能出现消息乱序，需配合幂等或 `max.in.flight.requests.per.connection=1`。

### Broker 不丢消息

```text
- replication.factor >= 3
- min.insync.replicas >= 2
- unclean.leader.election.enable=false（禁止非 ISR 副本当选 Leader）
```

### 消费者不丢消息

```text
- 关闭自动提交
- 先处理业务，再手动提交 offset
- 处理失败不提交，重试或进入死信
```

### 三种消息投递语义

| 语义 | 含义 |
|---|---|
| At Most Once | 最多一次，可能丢 |
| At Least Once | 至少一次，可能重复 |
| Exactly Once | 精确一次（生产端幂等 + 消费端事务/去重） |

**工程实践：** 大多数业务选择 At Least Once + 消费端幂等，实现简单且可靠。

---

## Q7. 幂等消费

### 为什么需要

Kafka 默认语义是 At Least Once：

```text
场景：消费者处理完消息但 offset 提交失败
→ 消费者重启后从旧 offset 重新消费
→ 同一消息被重复处理
```

### 解决方案

```text
1. 业务唯一键去重
   - 消息中带业务唯一 ID
   - 消费前查 Redis/DB，已处理则跳过
   - 处理成功后写入业务 ID

2. 数据库唯一约束
   - 利用唯一索引天然防重
   - 插入冲突即视为已处理

3. 数据库事务
   - 业务处理与 offset 提交放同一事务
   - 但 Kafka 不参与 DB 事务，需用幂等表

4. Redis SETNX + 过期时间
   - 适合短期防重场景
```

### 幂等消费的典型代码思路

```text
收到消息
  → 提取业务唯一 ID
  → 查 Redis：已存在 → 直接 ack 跳过
  → 不存在 → 处理业务 → 写入业务 ID → ack
```

---

## Q8. 消息堆积

### 常见原因

```text
1. 消费者处理速度跟不上生产速度
2. 消费者数量不足（分区数 > 消费者数）
3. 消费者代码性能差（慢查询、串行处理）
4. Rebalance 期间停止消费
5. 下游依赖故障（DB、第三方接口超时）
6. 单条消息处理耗时过长
```

### 排查思路

```text
1. 看消费者组 lag（消费延迟）
2. 看消费速率和消息处理耗时
3. 看是否有消费者掉线、Rebalance 频繁
4. 看下游依赖的健康度
5. 看消息大小和批量参数
```

### 解决方案

```text
紧急处理：
- 扩容消费者：增加消费者实例
- 增加分区数：提升并行上限
- 临时跳过非关键消息

长期优化：
- 消费逻辑异步化（先落库，异步处理）
- 批量消费、批量写库
- 优化消费端耗时逻辑
- 消息压缩，减小网络和磁盘开销
- 设置合理的 fetch 参数和批量参数
```

### 消息堆积带来的风险

```text
- 磁盘被写满，Broker 不可用
- 消费延迟过大，业务实时性受损
- 消息过期被删除，业务数据丢失
```

---

## Q9. 高频面试追问

| 追问 | 答案要点 |
|---|---|
| Kafka 为什么快 | 顺序写盘、页缓存、零拷贝、批量、分区并行 |
| 如何保证消息不丢 | 生产 `acks=all` + 重试，Broker 多副本，消费端先处理后提交 |
| 如何保证不重复消费 | 幂等消费，业务唯一键或唯一索引去重 |
| 如何保证消息顺序 | 分区内有序；相同 key 进同一分区；全局有序需单分区 |
| 消费者数量大于分区数会怎样 | 多余消费者空闲，不参与消费 |
| `acks=all` 是等所有副本吗 | 不是，是等 ISR 中所有副本 |
| Rebalance 触发条件 | 成员变化、分区变化、心跳超时 |
| 死信队列的作用 | 隔离无法处理的失败消息，防止阻塞正常消费 |

---

## Q10. RabbitMQ 核心特性

### 消息模型

```text
Producer → Exchange → Binding（路由规则）→ Queue → Consumer
```

RabbitMQ 的核心是 **Exchange 路由机制**，消息先到 Exchange，再按路由规则分发到队列。

### Exchange 四种类型

| 类型 | 路由规则 | 场景 |
|---|---|---|
| Direct | Routing Key 精确匹配 | 点对点、指定消费者 |
| Fanout | 广播到所有绑定队列 | 广播通知 |
| Topic | Routing Key 通配符匹配（`*` 一个词、`#` 多个词） | 按规则路由、灵活分发 |
| Headers | 按消息头匹配（较少使用） | 特殊场景 |

### 核心特性

```text
1. ACK 机制：消费者处理成功后 ack，失败 nack 可重回队列
2. 死信队列（DLX）：消息被拒、超时、队列满时进入死信队列
3. 延迟队列：TTL + DLX 组合实现，或使用延迟插件
4. 优先级队列：x-max-priority 声明
5. 消息持久化：Exchange、Queue、Message 三者都要 durable
6. 高可用：镜像队列（Mirror Queue）或仲裁队列（Quorum Queue）
7. 消息确认模式：自动确认、手动确认
8. 预取计数（prefetch）：控制推给消费者的未确认消息数量，实现能者多劳
```

### 延迟队列实现原理

```text
经典方案：TTL + DLX
- 正常队列不设消费者，设置消息 TTL
- 消息过期后投递到死信交换机
- 死信队列绑定真实消费者
- 实现"延迟消费"效果
```

### 可靠性保障

```text
生产者：
- Confirm 模式：消息到达 Broker 后回调确认
- 事务模式：性能差，较少使用

消费者：
- 手动 ACK，处理成功才 ack
- 配合持久化消息保证不丢

Broker：
- 队列和消息持久化
- 镜像/仲裁队列防止节点故障丢数据
```

---

## Q11. RocketMQ 核心特性

### 架构组成

```text
NameServer（注册中心，无状态，记录路由信息）
    ↓
Broker（Master/Slave 主从架构）
    ↓
Producer / Consumer
```

### 消息模型

```text
Topic（主题）
  ├─ Queue（队列，类似 Kafka 的分区）
  │    └─ 消息按顺序写入
  ├─ Tag（标签，二级过滤）
  └─ Message（业务消息）
```

**顺序消息：** 相同 key（如订单号）的消息发往同一 Queue，实现严格顺序消费。

### 核心特性

```text
1. 事务消息：两阶段提交 + 回查机制，保证本地事务与消息发送的一致性
2. 延迟消息：支持 18 个固定延迟级别，如 1s、5s、10s...
3. 顺序消息：全局顺序（单队列）或分区顺序
4. 消息过滤：Tag 过滤、SQL 表达式过滤
5. 死信队列：消费失败 16 次后进入死信 Topic
6. 消息重试：支持按延迟级别自动重试
7. 广播消费 / 集群消费两种模式
```

### 事务消息流程

```text
1. 发送 Half（半）消息，Broker 暂存但消费者不可见
2. 执行本地事务
3. 成功 → 提交，消息对消费者可见
   失败 → 回滚，消息删除
4. 超时未确认 → Broker 定期回查生产者本地事务状态
```

### 消息堆积处理

```text
- RocketMQ 消息默认保留 72 小时（可配置）
- 堆积时可扩容消费者、增加 Queue 数量
- 支持通过控制台查看消费进度和堆积情况
```

---

## Q12. 三款 MQ 详细对比

| 对比项 | Kafka | RocketMQ | RabbitMQ |
|---|---|---|---|
| 语言 | Scala/Java | Java | Erlang |
| 吞吐量 | 最高（百万级） | 高（十万级） | 中等（万级） |
| 延迟 | 毫秒级 | 毫秒级 | 微秒级 |
| 消息模型 | Topic/Partition | Topic/Queue/Tag | Exchange/Queue |
| 顺序消息 | 分区内有序 | 严格顺序支持 | 队列内有序 |
| 延迟消息 | 不支持原生 | 支持 18 个级别 | TTL+DLX 实现 |
| 事务消息 | 支持（幂等+事务） | 原生支持 | 支持（性能差） |
| 消息过滤 | 客户端过滤 | Tag、SQL 过滤 | Routing Key 规则 |
| 优先级队列 | 不支持 | 支持 | 支持 |
| 死信队列 | 无原生概念 | 原生支持 | 原生支持 |
| 消息回溯 | 支持（按 offset） | 支持（按时间） | 不支持（消费即删） |
| 存储 | 磁盘顺序写，默认保留 7 天 | 磁盘 + CommitLog，保留 72 小时 | 内存+磁盘，消费即删 |
| 集群 | 分区+副本 | 主从同步/异步 | 镜像/仲裁队列 |
| 适用场景 | 日志、大数据、流处理 | 电商、金融、事务消息 | 业务解耦、低延迟、灵活路由 |

### 一句话选型

```text
Kafka：大数据、日志、流计算、高吞吐场景
RocketMQ：电商、金融、事务消息、严格顺序场景
RabbitMQ：低延迟、灵活路由、中小规模业务解耦
```

---

## Q13. 高频对比追问

| 追问 | 答案要点 |
|---|---|
| 为什么 RocketMQ 适合电商 | 事务消息保证订单与消息一致性、延迟消息支持超时关单 |
| Kafka 为什么不适合延迟消息 | 无原生延迟投递，需外部定时器实现 |
| RabbitMQ 为什么延迟低 | 内存转发、Exchange 路由简单、协议轻量 |
| RocketMQ 和 Kafka 存储区别 | RocketMQ 所有消息写 CommitLog，Kafka 按分区写日志 |
| 消息回溯谁最强 | Kafka 按 offset 回溯最灵活，RocketMQ 按时间，RabbitMQ 基本不支持 |
| 三者的路由能力 | RabbitMQ 最强（4 种 Exchange），RocketMQ 有 Tag，Kafka 最弱 |
| 为什么 Kafka 吞吐最高 | 分区并行 + 顺序写 + 零拷贝 + 批量 |
| 选型核心考量 | 吞吐、延迟、事务、顺序、回溯、运维成本 |

---

## 附：关键配置速查

```text
生产端：
  acks=all
  retries=3
  enable.idempotence=true
  compression.type=lz4（或 zstd）

Broker 端：
  replication.factor=3
  min.insync.replicas=2
  unclean.leader.election.enable=false
  log.retention.hours=72（按需调整）

消费端：
  enable.auto.commit=false（手动提交）
  max.poll.records=500（按需调整）
  session.timeout.ms=30000
```
