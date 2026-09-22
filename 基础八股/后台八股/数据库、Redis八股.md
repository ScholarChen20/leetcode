# 数据库与 NoSQL 面试八股

> 整理日期：2026-09-08
> 方向：后台开发 / 关系型数据库 / NoSQL

---

# 第一部分：Redis

## R1. Redis 基本使用

### 五种基础数据类型

| 类型 | 结构 | 典型场景 |
|---|---|---|
| String | SDS 动态字符串 | 缓存、计数、分布式锁、Session |
| Hash | 哈希表 | 对象存储、购物车 |
| List | 双向链表/压缩列表 | 消息队列、时间线 |
| Set | 哈希表 | 去重、共同好友、抽奖 |
| ZSet | 跳表 + 哈希 | 排行榜、延迟队列 |

### 其他类型

```text
- Bitmap：签到、在线状态
- HyperLogLog：基数统计（UV）
- GEO：地理位置
- Stream：消息队列（消费者组、持久化）
```

### 为什么 Redis 快

```text
1. 纯内存操作
2. 单线程（6.0 前命令处理单线程）避免上下文切换和锁竞争
3. IO 多路复用（epoll）
4. 高效数据结构（跳表、压缩列表、SDS）
```

**注意：** Redis 6.0 引入多线程 IO（网络读写），命令执行仍是单线程。

### 常见应用场景

```text
缓存、分布式锁、计数器、排行榜、分布式 Session、
限流、消息队列、延迟队列、布隆过滤器
```

---

## R2. 缓存更新策略

### 经典三策略

| 策略 | 流程 | 问题 |
|---|---|---|
| Cache Aside（旁路缓存） | 读：先缓存后 DB；写：先 DB 后删缓存 | 最常用，需处理一致性问题 |
| Read/Write Through | 缓存层代理读写 DB | 实现复杂 |
| Write Behind（异步写回） | 先写缓存，异步批量写 DB | 可能丢数据 |

### Cache Aside 详解

```text
读请求：
  查缓存 → 命中直接返回
        → 未命中 → 查 DB → 写入缓存 → 返回

写请求：
  更新 DB → 删除缓存
```

### 为什么是"删除缓存"而不是"更新缓存"

```text
1. 更新缓存可能出现并发写覆盖，导致缓存是脏数据
2. 删除缓存让下次读请求重建，逻辑简单
3. 缓存可能不是简单字段映射，更新成本高
```

### 先删缓存 vs 先更新 DB

```text
先删缓存 + 后更新 DB：
- 问题：删缓存后、更新 DB 前，其他请求读到旧 DB 值并写入缓存 → 脏数据
- 解决：延迟双删（更新 DB 后延迟再删一次）

先更新 DB + 后删缓存：
- 问题：更新 DB 后、删缓存前，读请求读到旧缓存 → 短暂不一致
- 特点：不一致窗口小，主流选择
```


### Read/Write Through 与 Write Behind

- Read/Write Through：由缓存层统一代理读写，缓存未命中时读取 DB，写入时同步更新缓存和 DB，业务代码更简单，但缓存层实现复杂。
- Write Behind：先更新缓存，再异步批量写入 DB，吞吐量高，但服务宕机时可能丢数据，适合对实时持久化要求不高的场景。
### 缓存常见问题

| 问题 | 描述 | 解决 |
|---|---|---|
| 缓存穿透 | 查询不存在的数据，每次都打 DB | 缓存空值、布隆过滤器 |
| 缓存击穿 | 热点 key 过期瞬间大量请求打 DB | 互斥锁、逻辑过期、热点不过期 |
| 缓存雪崩 | 大量 key 同时过期或 Redis 宕机 | 过期时间加随机值、集群、多级缓存 |
| 缓存一致性问题 | DB 与缓存数据不一致 | 延迟双删、版本号、订阅 binlog |

### 最终一致性方案

```text
- 延迟双删
- 订阅 MySQL binlog（Canal）异步更新缓存
- 版本号/时间戳校验
```

---

## R3. 持久化机制

### RDB（快照）

```text
原理：某个时间点全量数据快照写入磁盘
触发：save（阻塞）/ bgsave（fork 子进程）/ 配置定时
优点：恢复快、文件紧凑
缺点：两次快照之间可能丢数据、fork 大内存开销
```

### AOF（追加日志）

```text
原理：记录每条写命令，追加写入文件
同步策略：
  always：每条命令刷盘，最安全最慢
  everysec：每秒刷盘，最多丢 1 秒数据（默认）
  no：交给操作系统，性能最好
```

### AOF 重写机制

```text
问题：AOF 文件持续增长
方案：bgrewriteaof，fork 子进程按当前数据生成最小命令集
```

### 混合持久化（Redis 4.0+）

```text
RDB 快照 + AOF 增量日志组合
恢复时先加载 RDB，再重放后续 AOF
```

### 选择建议

```text
- 允许分钟级丢失：RDB
- 允许秒级丢失：RDB + AOF（everysec）
- 混合持久化：生产环境主流选择
```

---

## R4. 内存管理

### 内存淘汰策略

| 策略 | 行为 |
|---|---|
| noeviction | 不淘汰，写满报错（默认） |
| allkeys-lru | 所有 key 中淘汰最久未使用 |
| volatile-lru | 带过期时间的 key 中淘汰 LRU |
| allkeys-lfu | 所有 key 中淘汰使用频率最低 |
| volatile-lfu | 带过期时间的 key 中淘汰 LFU |
| allkeys-random | 随机淘汰 |
| volatile-random | 带过期时间随机淘汰 |
| volatile-ttl | 淘汰即将过期的 key |

### LRU 与 LFU 区别

```text
LRU：最近最少使用，按"最近访问时间"淘汰
LFU：最不经常使用，按"访问频率"淘汰
适合场景：
- LRU：通用缓存
- LFU：热点数据保护（如热门商品）
```

### 过期键删除策略

```text
惰性删除：访问时检查是否过期，过期则删
定期删除：定期随机抽查一批 key 检查过期
两者结合：Redis 默认策略
```

### 内存碎片与优化

```text
- 使用相同大小、结构一致的数据
- 避免频繁修改大 value
- jemalloc 分配器
```

---

## R5. 集群

### 三种集群方案

| 方案 | 特点 | 适用 |
|---|---|---|
| 主从复制 | 一主多从，读写分离 | 简单场景、读多写少 |
| 哨兵 Sentinel | 主从 + 自动故障转移 | 高可用、中小规模 |
| Cluster | 分片存储，多主多从 | 大数据量、高吞吐 |

### 主从复制流程

```text
1. 从节点连接主节点，发送 PSYNC
2. 全量同步：主生成 RDB 发给从
3. 增量同步：主持续发送写命令
4. 复制积压缓冲区支持断线续传
```

### Sentinel 哨兵机制

```text
职责：
- 监控主从节点健康
- 主节点故障时自动选举新主
- 通知客户端新主地址

选举过程：
- 主观下线（单个哨兵认为主挂）
- 客观下线（多数哨兵投票确认）
- 选举 Leader 哨兵执行故障转移
- 选新主：优先复制偏移量最大的从节点
```

### Redis Cluster

```text
- 16384 个哈希槽（slot），数据按 key 哈希到槽
- 每个节点负责一部分槽
- 客户端根据 key 计算槽，直接访问对应节点
- 主从结构保证高可用
- 节点间 gossip 协议通信
```

### 集群相关问题

```text
- 多 key 操作需在同一槽（hash tag {user}:1）
- 不支持跨节点事务
- 扩容迁移槽：reshard
```

---

## R6. 分布式锁

### SETNX 方案的问题

```text
SETNX key value + expire key seconds
问题：
1. SETNX 与 expire 非原子，中间宕机锁永不过期
2. 误删别人的锁：A 业务超时，B 拿到锁，A 删了 B 的锁
```

### 正确姿势

```text
SET key value NX EX seconds（原子设置锁和过期时间）
value 使用唯一标识（UUID/线程 ID）

释放锁：
Lua 脚本先判断 value 是否为自己，是才删除
保证"判断 + 删除"原子性
```

### Redisson 方案

```text
- 看门狗（watchdog）自动续期，默认 30 秒续一次
- 可重入锁：hash 结构记录重入次数
- 红锁（RedLock）：多节点投票，争议较大
```


### Redisson 延迟队列原理

Redisson 的 RDelayedQueue 通常基于 Redis 的 Sorted Set 实现：

1. 将任务放入 Sorted Set；
2. 用 score 保存任务的到期时间；
3. 定期扫描已经到期的任务；
4. 将到期任务从 Sorted Set 转移到就绪队列；
5. 消费者从阻塞队列中获取并处理任务。

**面试结论：** Sorted Set 负责按时间排序，阻塞队列负责通知和消费；它适合延迟任务，但不等同于严格实时的定时调度系统。
### 常见问题

```text
1. 锁过期但业务未完成 → 续期机制（看门狗）
2. 释放了别人的锁 → value 校验
3. 主从切换丢锁 → 红锁或 Zookeeper
4. 不可重入 → hash 计数实现
```

---

# 第二部分：MySQL

## M1. 索引

### 索引类型

| 类型 | 说明 |
|---|---|
| B+Tree 索引 | InnoDB 默认，最常用 |
| Hash 索引 | 等值查询快，不支持范围 |
| 全文索引 | 文本搜索 |
| 空间索引 | 地理位置数据 |

### B+Tree 特点

```text
1. 非叶子节点只存键，叶子节点存完整数据
2. 叶子节点用双向链表连接，支持范围查询
3. 高度低（3-4 层可存千万级数据）
4. 数据有序，天然支持排序
```

### 聚簇索引 vs 非聚簇索引

| 索引 | 叶子节点内容 | 特点 |
|---|---|---|
| 聚簇索引（主键） | 完整行数据 | 每表一个，主键即聚簇索引 |
| 二级索引 | 索引键 + 主键值 | 回表查询完整数据 |

### 回表与覆盖索引

```text
回表：二级索引找到主键，再去聚簇索引查完整行
覆盖索引：查询字段全在二级索引中，无需回表
优化：select 需要的字段 + 建立覆盖索引
```

### 最左前缀原则

```text
联合索引 (a, b, c)：
- where a = ? ✓
- where a = ? and b = ? ✓
- where b = ? ✗（跳过 a 无法使用）
- where a = ? and c = ? 只能用 a（b 断了）
```


### 索引下推 ICP

索引下推（Index Condition Pushdown，ICP）允许存储引擎在遍历二级索引时，直接判断部分 WHERE 条件，先过滤不满足的记录，再回表查询，从而减少回表次数。

**面试结论：** 能在索引层过滤，就不要全部回表后再过滤。

### 索引失效的底层原因

索引依赖 B+Tree 的有序性和最左前缀规则。以下写法会让 MySQL 无法快速定位索引范围，或只能扫描后过滤：

- 跳过联合索引的前导列；
- 对索引列使用函数或计算；
- 发生隐式类型转换；
- LIKE 左侧使用通配符；
- OR 两侧无法有效使用索引；
- ORDER BY 无法利用索引，出现 Using filesort。
### 索引失效场景

```text
1. 对索引列使用函数或计算：where year(create_time) = 2024
2. 隐式类型转换：字符串列用数字查询
3. like '%xx' 左模糊
4. OR 连接非索引列
5. 联合索引不满足最左前缀
6. 索引列使用不等于（!=、<>、not in）
```

### 索引设计原则

```text
1. 区分度高的列放前面
2. 联合索引覆盖常用查询
3. 索引不是越多越好（写放大）
4. 频繁更新的列慎重加索引
```

---

## M2. 存储引擎

### InnoDB vs MyISAM

| 对比项 | InnoDB | MyISAM |
|---|---|---|
| 事务 | 支持 | 不支持 |
| 行级锁 | 支持 | 表级锁 |
| 外键 | 支持 | 不支持 |
| MVCC | 支持 | 不支持 |
| 崩溃恢复 | redo log 支持 | 不支持 |
| 全文索引 | 5.6+ 支持 | 支持 |
| 数据存储 | 表空间 | 三个文件（.frm/.MYD/.MYI） |
| 适用场景 | 通用、OLTP | 只读、统计报表 |

### InnoDB 内存结构

```text
Buffer Pool（缓冲池）：
- 缓存数据页和索引页
- 写请求先写 Buffer Pool，异步刷盘
- 是 InnoDB 最重要的内存结构
```

---

## M3. 事务

### ACID

| 特性 | 含义 | MySQL 实现 |
|---|---|---|
| 原子性 | 全部成功或全部失败 | undo log |
| 一致性 | 数据状态合法 | 其他三者共同保证 |
| 隔离性 | 事务之间互不影响 | 锁 + MVCC |
| 持久性 | 提交后不丢失 | redo log |

### 隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不会 | 可能 | 可能 |
| REPEATABLE READ（默认） | 不会 | 不会 | 可能（MVCC 基本解决） |
| SERIALIZABLE | 不会 | 不会 | 不会 |

**脏读：** 读到未提交的数据
**不可重复读：** 同一事务两次读同一条数据结果不同
**幻读：** 同一事务两次查询的记录数量不同

### 事务传播行为（Spring）

```text
REQUIRED：有事务则加入，没有则新建（默认）
REQUIRES_NEW：总是新建独立事务
SUPPORTS / NOT_SUPPORTED / MANDATORY / NEVER / NESTED
```

---

## M4. MVCC（多版本并发控制）
是数据库通过“保存数据多个版本”来实现并发控制的机制。MySQL InnoDB 中，MVCC 主要用于提高读写并发，减少读操作对写操作的阻塞。
MVCC 通过 undo log + Read View + 多版本数据 实现非阻塞快照读；锁机制则负责控制当前读和写操作之间的并发冲突。
### 实现原理

```text
1. 隐藏字段：
   - trx_id：最近修改的事务 ID
   - roll_pointer：指向 undo log 旧版本
   - row_id：无主键时的隐藏主键

2. Undo Log：记录数据旧版本，形成版本链

3. Read View：快照，记录当前活跃事务列表
   - creator_trx_id：创建者事务 ID
   - min_trx_id：活跃事务最小 ID
   - max_trx_id：下一个待分配事务 ID
   - m_ids：活跃事务 ID 集合
```

### 可见性判断规则

```text
数据版本 trx_id 与 Read View 比较：
1. trx_id < min_trx_id → 已提交，可见
2. trx_id >= max_trx_id → 未开始，不可见
3. trx_id 在 m_ids 中 → 未提交，不可见
4. 否则 → 已提交，可见
不可见时沿 roll_pointer 回退到上一版本继续判断
```

### 快照读 vs 当前读

```text
快照读（普通 select）：读 Read View 快照，不加锁
当前读（select for update / update / delete）：读最新数据，加锁


```

---

## M5. 锁

### 锁类型

| 分类 | 锁 | 说明 |
|---|---|---|
| 粒度 | 表锁 / 行锁 / 页锁 | InnoDB 支持行锁 |
| 模式 | 共享锁 S / 排他锁 X | 读共享、写互斥 |
| 算法 | Record / Gap / Next-Key | 行锁、间隙锁、组合锁 |

### 行锁算法

```text
Record Lock：锁定单条记录
Gap Lock：锁定记录之间的间隙，防止插入
Next-Key Lock：Record + Gap，左开右闭区间
主要目的：解决 RR 隔离级别下的幻读
```

### 死锁

```text
原因：两个事务互相等待对方持有的锁
检测：InnoDB 等待图检测，自动回滚代价小的事务
避免：
- 按相同顺序访问资源
- 尽量缩短事务
- 使用合理索引，减少锁范围
```

### 乐观锁 vs 悲观锁

```text
悲观锁：假定会冲突，先加锁再操作（for update）
乐观锁：假定不冲突，提交时检查（版本号/时间戳）
适用：
- 冲突多 → 悲观锁
- 冲突少 → 乐观锁
```

---

## M6. 日志

### 三种日志

| 日志 | 层次 | 作用 |
|---|---|---|
| redo log | InnoDB 引擎层 | 崩溃恢复，保证持久性 |
| undo log | InnoDB 引擎层 | 事务回滚、MVCC |
| binlog | MySQL Server 层 | 主从复制、数据恢复 |

### redo log

```text
- 物理日志：记录数据页的修改
- 循环写：固定大小，写满循环覆盖
- WAL（Write-Ahead Logging）：先写日志再写数据页
- 刷盘参数 innodb_flush_log_at_trx_commit：
  0：每秒刷盘，可能丢 1 秒
  1：每次提交刷盘（默认，安全）
  2：每次提交写 OS 缓存
```

### binlog

```text
- 逻辑日志：记录 SQL 语句或行变更
- 追加写：文件写满滚动
- 格式：STATEMENT / ROW / MIXED
- 用途：主从复制、数据恢复（如误删恢复）
```


### redo log、undo log、binlog 的职责

- redo log：InnoDB 引擎层的物理日志，用于崩溃恢复，保证持久性；
- undo log：InnoDB 引擎层的回滚日志，用于事务回滚和 MVCC；
- binlog：MySQL Server 层的逻辑日志，用于主从复制和数据恢复。

MySQL 的备份、主从和主备同步主要依赖 binlog；事务出错或回滚时，InnoDB 利用 undo log 恢复旧版本数据。

### 更新语句为什么需要两阶段提交？

更新语句大致流程：

    执行器
      ↓
    redo log prepare
      ↓
    写 binlog
      ↓
    redo log commit

这样可以保证 redo log 和 binlog 状态一致，避免主库已经提交但 binlog 没记录，或者 binlog 已记录但引擎事务未提交。
### 两阶段提交

```text
更新流程：
1. 写 redo log（prepare 状态）
2. 写 binlog
3. redo log 标记 commit

目的：保证 redo log 与 binlog 一致，主从数据不丢失
```

---

## M7. SQL 优化


### SQL 语句的执行流程

**查询语句：**

    客户端 → 连接器 → 权限校验 → 分析器 → 优化器 → 执行器 → 存储引擎

**更新语句：**

    连接器 → 权限校验 → 分析器 → 优化器 → 执行器
                              ↓
    存储引擎 → redo log prepare → binlog → redo log commit

查询缓存已在 MySQL 8.0 中移除，不应再把查询缓存作为当前 MySQL 的通用执行步骤。
### 执行计划（EXPLAIN）

```text
关键字段：
type：访问类型，性能从好到差
  system > const > eq_ref > ref > range > index > ALL
possible_keys：候选索引
key：实际使用的索引
rows：预估扫描行数
Extra：Using index（覆盖索引）/ Using filesort（需优化）/ Using temporary（临时表）
```

### 优化方向

```text
1. 索引优化：合适索引、覆盖索引、避免失效
2. 查询优化：
   - select 具体字段，避免 select *
   - 大分页：延迟关联/游标
   - 避免子查询，用 join
3. 表结构优化：
   - 字段类型最小化
   - 避免大字段（text/blob）频繁查询
4. SQL 写法：
   - 小表驱动大表
   - in 数量控制
   - 避免函数操作索引列
```

### 大分页优化

```text
select * from t limit 1000000, 10

优化方案：
1. 延迟关联：先查主键，再回表
2. where id > 上次最大 id（游标分页）
```

### 慢查询排查流程

```text
1. 开启慢查询日志，定位慢 SQL
2. EXPLAIN 分析执行计划
3. 检查索引使用情况
4. 优化 SQL 或索引
5. 必要时分库分表
```

---

# 第三部分：MongoDB

## N1. MongoDB 基础

### 核心概念对比

| MongoDB | MySQL |
|---|---|
| Database | Database |
| Collection | Table |
| Document | Row |
| Field | Column |
| `_id` | 主键 |
| 内嵌文档 | Join 关联表 |

### 特性

```text
1. 文档模型：JSON/BSON 格式，灵活 Schema
2. 水平扩展：分片（sharding）
3. 丰富查询：字段、范围、数组、嵌套文档
4. 聚合管道：分组、统计、转换
5. 地理空间索引
```

### 适用场景

```text
- 内容管理、日志、物联网数据
- 灵活 Schema 的快速迭代业务
- 大量写入、低一致性要求的场景
- 内嵌文档模式（1:1、1:N 少关联）
```

### 不适合场景

```text
- 强事务关联（多表 join）
- 复杂事务一致性要求高
- 需要严格外键约束
```

---

## N2. MongoDB 索引与副本集

### 索引类型

```text
单字段索引、复合索引、多键索引（数组字段）、
文本索引、地理空间索引、TTL 索引
```

### 副本集（Replica Set）

```text
- Primary：处理读写
- Secondary：同步数据，可读（需配置）
- 自动故障转移：Primary 挂掉，自动选举新 Primary
```

### 分片（Sharding）

```text
- Shard Key：分片键
- 数据按 shard key 分布到多个分片
- 支持水平扩展
- 分片键选择影响数据分布均匀性
```

---

# 第四部分：ElasticSearch

## E1. ES 基础

### 核心概念

```text
Index（索引）：类似数据库的库
Type（类型）：7.x 已废弃，一个 Index 一个 Type
Document（文档）：一行记录，JSON 格式
Mapping：字段类型定义
Shard：分片，水平扩展单元
Replica：副本，高可用
```

### 与 MySQL 概念对比

| ES | MySQL |
|---|---|
| Index | Database |
| Type（废弃） | Table |
| Document | Row |
| Field | Column |
| Mapping | Schema |

### 为什么快

```text
1. 倒排索引：词 → 文档 ID 列表，全文检索 O(1) 定位
2. 分布式：数据分片到多节点并行检索
3. 内存缓存：文件系统缓存
4. 相关性排序：TF-IDF / BM25
```

---

## E2. 倒排索引原理

```text
正向索引：文档 → 词列表
倒排索引：词 → 文档列表

例：
Doc1: "the quick brown fox"
Doc2: "the lazy dog"

倒排索引：
the   → [Doc1, Doc2]
quick → [Doc1]
brown → [Doc1]
fox   → [Doc1]
lazy  → [Doc2]
dog   → [Doc2]
```

### 写入流程

```text
写入 → 内存 Buffer → refresh（1s）→ Segment 可搜索
     → translog（防丢失）→ flush → 磁盘
```

**refresh 机制：** 默认 1 秒，所以 ES 写入后要等约 1 秒才能搜到（准实时）。

---

## E3. 与关系型数据库的选择

```text
ES 擅长：全文搜索、模糊匹配、聚合分析、海量数据检索
MySQL 擅长：事务、关联查询、精确读写

典型架构：MySQL 做存储，ES 做检索
数据同步：binlog（Canal）异步同步到 ES
```

---

## 附：高频对比追问

| 追问 | 答案要点 |
|---|---|
| Redis 和 MySQL 数据一致性 | 删除缓存、延迟双删、binlog 同步 |
| Redis 为什么用跳表 | ZSet 范围查询 O(logN) |
| MySQL RR 为什么默认 | 兼顾一致性与性能，MVCC 解决大部分幻读 |
| redo log 和 binlog 区别 | 引擎层/Server 层、物理/逻辑、循环/追加 |
| MongoDB 为什么快 | 文档模型、内存映射、无 join |
| ES 为什么快 | 倒排索引、分布式并行、缓存 |
| ES 和 MongoDB 都存 JSON 区别 | ES 重检索分析，MongoDB 重灵活存储 |
---
