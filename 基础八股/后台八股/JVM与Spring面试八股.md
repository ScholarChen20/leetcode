# JVM 与 Spring 全家桶面试八股

> 方向：后台开发 / JVM / Spring
> 用法：先看每节的「一句话结论」，再看原理和追问；表格用于横向对比记忆。

## 目录

- 第一部分 JVM：J1 架构 · J2 运行时数据区 · J3 堆与分代 · J4 对象创建 · J5 对象布局与访问 · J6 对象存活判定 · J7 GC 算法 · J8 分代回收与晋升 · J9 垃圾收集器 · J10 类加载过程 · J11 类加载器与双亲委派 · J12 调优与排查
- 第二部分 Spring：S1 IoC 与 DI · S2 AOP · S3 Bean 生命周期 · S4 循环依赖 · S5 事务 · S6 自动装配 · S7 Spring Boot 启动原理 · S8 Spring MVC 请求流程 · S9 高频追问

---

# 第一部分：JVM

## J1. JVM 整体架构

**一句话结论：** JVM 由「类加载子系统 + 运行时数据区 + 执行引擎」三块核心组成，外挂本地方法接口。

    ┌────────────────────────────────────────────┐
    │                类加载子系统                │
    │     加载 → 验证 → 准备 → 解析 → 初始化     │
    └─────────────────────┬──────────────────────┘
                          │ 生成 Class 对象、放入方法区
    ┌─────────────────────▼──────────────────────┐
    │                运行时数据区                │
    │    线程私有：PC / 虚拟机栈 / 本地方法栈    │
    │      线程共享：堆 / 方法区（元空间）       │
    └─────────────────────┬──────────────────────┘
                          │ 字节码
    ┌─────────────────────▼──────────────────────┐
    │                  执行引擎                  │
    │     解释器 + JIT 即时编译 + 垃圾收集器     │
    └─────────────────────┬──────────────────────┘
                          │
                          ▼
            本地库接口（JNI）→ 本地方法库

关键理解：

- **跨平台的本质**：字节码是 JVM 的"机器码"，JVM 才是各平台的具体实现；
- **解释器 + JIT 混合**：解释器保证启动快，JIT 把热点代码编译成本地机器码保证运行快，两者互补；
- **垃圾收集器是执行引擎的一部分**，不是独立模块，它是后台线程在跑。

---

## J2. JVM 内存模型（运行时数据区）

**一句话结论：** 五个区，三个线程私有、两个线程共享；只有程序计数器不会 OOM。

| 区域 | 线程归属 | 存放内容 | 异常 |
|---|---|---|---|
| 程序计数器 PC | 私有 | 当前线程执行字节码的行号指示器 | 唯一不会抛 OOM |
| 虚拟机栈 | 私有 | 栈帧：局部变量表、操作数栈、动态链接、方法返回地址 | StackOverflowError / OOM |
| 本地方法栈 | 私有 | native 方法调用 | StackOverflowError / OOM |
| 堆 | 共享 | 对象实例、数组 | OutOfMemoryError: Java heap space |
| 方法区（元空间） | 共享 | 类元信息、运行时常量池、静态变量、JIT 编译后的代码 | OOM: Metaspace |

补充两个常被忽略的区域：

- **运行时常量池**：方法区的一部分，存放编译期生成的字面量和符号引用。JDK 7 起**字符串常量池**被移到了堆里（`String.intern()` 的考点来源）；
- **直接内存**：不是 JVM 运行时数据区的一部分，NIO 的 `DirectByteBuffer` 用的就是它，受物理内存限制，也会 OOM。

**方法区的演进（高频追问）：**

    JDK 7 及以前：永久代 PermGen，在堆内，受 -XX:MaxPermSize 限制，易 OOM
    JDK 8 开始  ：元空间 Metaspace，移到本地内存，受 -XX:MaxMetaspaceSize 限制

为什么改：永久代大小难预估、Full GC 效率低、与 JRockit 合并的需要。

**追问：堆和栈的区别？**

- **堆**：存对象，线程共享，由 GC 管理，空间大，分配相对慢；
- **栈**：存方法调用（栈帧），线程私有，随方法进出自动释放，空间小，分配快。

**追问：什么情况 StackOverflow、什么情况 OOM？**

- 无限递归、栈帧过大 → `StackOverflowError`（栈深度超限）；
- 对象持续增长且无法回收 → `OutOfMemoryError: Java heap space`；
- 动态生成类过多（CGLIB、反射、热部署）→ `OutOfMemoryError: Metaspace`。

---

## J3. 堆结构与分代

**一句话结论：** 堆分新生代（Eden + 两个 Survivor）和老年代，默认比例 1:2，新生代内部 8:1:1。

    新生代（约 1/3）              老年代（约 2/3）
    ┌─────────┬──────┬──────┐    ┌──────────────────────┐
    │  Eden   │  S0  │  S1  │    │ 长期存活对象、大对象 │
    └─────────┴──────┴──────┘    └──────────────────────┘
         8        1      1

相关参数：

| 参数 | 含义 | 默认 |
|---|---|---|
| -Xms / -Xmx | 初始 / 最大堆大小 | 物理内存 1/64、1/4 |
| -Xmn | 新生代大小 | — |
| -XX:NewRatio | 老年代 : 新生代 | 2（即新生代占 1/3） |
| -XX:SurvivorRatio | Eden : 单个 Survivor | 8 |
| -XX:MaxTenuringThreshold | 晋升老年代的年龄阈值 | 15 |
| -XX:PretenureSizeThreshold | 超过该大小的对象直接进老年代 | 0（不启用） |

**为什么 Survivor 是 8:1:1？** 因为新生代对象绝大多数朝生夕死，存活率很低。留 10% 的空间足够容纳存活对象，这样可用空间达到 90%，而不是复制算法的理论 50%。代价是需要"空间分配担保"兜底。

**为什么需要两个 Survivor？** 保证复制算法能连续工作：Eden + S0 的存活对象复制到 S1，然后 Eden 和 S0 整体清空；下一轮 Eden + S1 复制到 S0。始终有一块 Survivor 是空的。

**TLAB（常被追问）：** 堆是共享的，多线程同时分配对象需要同步。JVM 在 Eden 中给每个线程预先划一小块私有区域 TLAB，线程在自己的 TLAB 里分配不需要加锁，用完再申请新的。

---

## J4. 对象创建过程

**一句话结论：** 类加载检查 → 分配内存 → 零值初始化 → 设置对象头 → 执行构造方法。

    1. 类加载检查
       new 指令 → 常量池定位类的符号引用 → 检查是否已加载/解析/初始化
       未加载则先触发类加载

    2. 分配内存
       指针碰撞：内存规整时，指针往后挪（Serial、ParNew + 标记整理/复制）
       空闲列表：内存不规整时，从空闲列表找一块（CMS + 标记清除）
       并发安全：CAS + 失败重试，或者 TLAB

    3. 内存初始化为零值
       保证实例字段不显式赋值也能直接用（int=0, 引用=null）

    4. 设置对象头
       Mark Word：hashCode、GC 分代年龄、锁状态标志
       类型指针：指向方法区的类元信息

    5. 执行 <init> 构造方法
       真正按代码里的赋值和构造函数执行

**注意顺序考点：** 第 3 步的零值初始化发生在构造方法之前，所以"成员变量有默认值、局部变量必须显式初始化"的根因在这里。第 4 步设置对象头时 hashCode 通常还没算，第一次调用 `hashCode()` 或 `System.identityHashCode()` 时才算出来并写入。

**追问：分配内存时如何保证线程安全？**

    方案一：CAS + 失败重试，直接对分配指针做原子更新
    方案二：TLAB，每个线程在 Eden 里预分配一块私有缓冲区，本地分配无需同步
    HotSpot 默认两者都用：优先 TLAB，TLAB 用完再走 CAS 申请新块

---

## J5. 对象内存布局与访问定位

对象在内存中的三部分：

| 部分 | 内容 |
|---|---|
| 对象头 | Mark Word（8 字节，hash、分代年龄、锁标志）+ 类型指针（4/8 字节，压缩指针下 4 字节）；数组对象还有 4 字节长度 |
| 实例数据 | 父类继承字段 + 本类字段，同宽度的字段会被放在一起以节省空间 |
| 对齐填充 | 保证对象大小是 8 字节的整数倍 |

**Mark Word 在不同锁状态下的内容**（和 synchronized 锁升级直接相关）：

| 锁状态 | 存储内容 | 标志位 |
|---|---|---|
| 无锁 | hashCode + 分代年龄 | 01 |
| 偏向锁 | 线程 ID + epoch + 分代年龄 | 01 |
| 轻量级锁 | 指向栈中 Lock Record 的指针 | 00 |
| 重量级锁 | 指向 ObjectMonitor 的指针 | 10 |
| GC 标记 | 空（内容被 GC 复用） | 11 |

**对象访问定位的两种方式：**

- **句柄访问**：堆中划出一块句柄池，引用指向句柄，句柄中分别存对象实例指针和类型数据指针。
  优点：对象被 GC 移动时只需改句柄，引用本身保持稳定；缺点是每次访问多一次间接寻址。
- **直接指针**：引用直接指向对象，对象头里存类型指针。
  优点：少一次寻址，访问更快 → **HotSpot 采用这种**。

---

## J6. 如何判断对象是否存活

**一句话结论：** Java 用可达性分析，不用引用计数；从 GC Roots 出发不可达的对象才可回收。

### 两种算法对比

| 算法 | 原理 | 问题 | Java 是否采用 |
|---|---|---|---|
| 引用计数 | 每个对象维护一个计数器，被引用 +1，引用失效 -1，为 0 即回收 | 无法解决循环引用；计数更新有开销 | 否（Python 用） |
| 可达性分析 | 从 GC Roots 出发遍历引用链，不可达即可回收 | 需要 STW 保证一致性快照 | 是 |

### GC Roots 包括哪些

- **虚拟机栈中局部变量表引用的对象**（正在执行的方法的参数、局部变量、临时变量）
- **方法区中类静态属性引用的对象**（`static` 变量）
- **方法区中常量引用的对象**（`final` 常量、字符串常量池里的引用）
- **本地方法栈中 JNI 引用的对象**
- **JVM 内部引用**：基本类型的 Class 对象、常驻异常对象（如 NPE）、系统类加载器
- **被 synchronized 持有的对象**
- **临时性加入**：分代收集时，老年代对象可能引用新生代对象，此时老年代的这部分对象也会被临时加入 GC Roots（配合卡表/记忆集）

**记忆口诀：** 「两栈两static，加上锁和内部类」——栈、本地方法栈、静态属性、常量，再加锁对象和 JVM 内部引用。

### 四种引用类型

| 类型 | 类 | 回收时机 | 典型用途 |
|---|---|---|---|
| 强引用 | 普通 `new` | 永远不回收，宁可 OOM | 绝大多数场景 |
| 软引用 | SoftReference | 内存不足时回收 | 缓存（图片、页面） |
| 弱引用 | WeakReference | 下次 GC 就回收 | ThreadLocalMap 的 key、WeakHashMap |
| 虚引用 | PhantomReference | 随时可能被回收，无法通过它取到对象 | 配合 ReferenceQueue 做回收通知（如 DirectByteBuffer 释放堆外内存） |

### 对象"死亡"的完整流程

    第一次标记：可达性分析不可达 → 标记
        ↓
    筛选：是否有必要执行 finalize()
        ├── 没有覆盖 finalize / 已被调用过 → 直接回收
        └── 需要执行 → 放入 F-Queue，由 Finalizer 线程低优先级执行
                ↓
    第二次标记：执行 finalize 后仍未重新建立引用 → 真正回收

**面试建议：** 知道 finalize 存在、知道它不保证执行、已被标记为 deprecated（JDK 9 起），业务代码不要依赖它。

---

## J7. 垃圾收集算法

| 算法 | 做法 | 优点 | 缺点 | 典型使用者 |
|---|---|---|---|---|
| 标记-清除 | 标记存活对象，直接清除未标记的 | 实现简单，不需要移动对象 | 内存碎片；标记和清除效率都不高 | CMS |
| 复制 | 把存活对象复制到另一半空间，整块清空原空间 | 无碎片，分配用指针碰撞很快 | 可用内存减半，存活对象多时复制成本高 | 新生代（Serial/ParNew/Parallel） |
| 标记-整理 | 标记存活对象并全部向一端移动 | 无碎片，不浪费空间 | 移动对象需要 STW，成本高 | 老年代（Serial Old/Parallel Old） |
| 分代收集 | 按对象存活周期分区，各用最合适的算法 | 扬长避短，是主流实践 | 实现复杂，需要跨代引用处理 | 几乎所有商用 JVM |

**分代的核心前提（弱分代假说）：** 绝大多数对象都是朝生夕死的，熬过越多次 GC 的对象越难死。所以新生代用复制（存活少，复制便宜），老年代用标记-整理或标记-清除（存活多，不值得复制）。

### 三色标记法与并发标记的问题（进阶加分项）

并发标记阶段用户线程还在跑，引用关系会变，于是有了三色标记：

    白色：未访问（如果标记结束还是白色，就是垃圾）
    灰色：自身已访问，但引用的对象还没全部扫描完
    黑色：自身和所有引用都已扫描完

并发时可能发生**对象消失**（漏标），必须同时满足两个条件：

1. 黑色对象新增了指向白色对象的引用（赋值器插入了一条或多条新引用）
2. 所有指向该白色对象的灰色引用被删除（赋值器删除了）

两种解决方案：

- **增量更新（Incremental Update）**：记录新增的引用，重新标记时以这些黑色对象为根再扫一遍 → **CMS 采用**
- **原始快照（SATB, Snapshot At The Beginning）**：记录删除的引用，按开始时的快照处理，把被删的引用当作还活着 → **G1、Shenandoah 采用**

---

## J8. 分代回收流程与对象晋升

**Minor GC 的完整过程：**

    新对象优先在 Eden 分配
        ↓
    Eden 满 → 触发 Minor GC（只回收新生代，速度快）
        ↓
    Eden + 当前 Survivor 的存活对象 → 复制到另一块 Survivor
        ↓
    对象年龄 +1（存在对象头的 Mark Word 里）
        ↓
    达到晋升条件 → 移到老年代

**四种"提前"进入老年代的情况（高频追问）：**

| 条件 | 说明 | 参数 |
|---|---|---|
| 年龄达标 | 每经历一次 Minor GC 年龄 +1，默认 15 | -XX:MaxTenuringThreshold |
| 大对象 | 超过阈值直接进老年代，避免在 Survivor 反复复制 | -XX:PretenureSizeThreshold |
| 动态年龄判定 | Survivor 中**同年龄**对象大小总和超过 Survivor 的一半，则大于等于该年龄的直接晋升 | -XX:TargetSurvivorRatio |
| 空间分配担保 | Minor GC 前检查老年代剩余连续空间是否够用，不够则改为 Full GC | -XX:-HandlePromotionFailure |

**GC 类型区分：**

    Minor GC / Young GC：只回收新生代，频繁但快
    Major GC / Old GC  ：只回收老年代（目前只有 CMS 有独立的老年代回收）
    Mixed GC           ：G1 特有，回收整个新生代 + 部分老年代 Region
    Full GC            ：回收整个堆 + 方法区，最慢，要尽量避免

**Full GC 的常见触发原因（排查必备）：**

- 老年代空间不足（对象晋升过快、大对象过多）
- 元空间不足（动态生成类过多）
- 空间分配担保失败
- CMS 出现 Concurrent Mode Failure
- 显式调用 `System.gc()`（可用 -XX:+DisableExplicitGC 屏蔽）

---

## J9. 垃圾收集器

### 总览

| 收集器 | 区域 | 算法 | 线程 | 特点 | 状态 |
|---|---|---|---|---|---|
| Serial | 新生代 | 复制 | 单线程 | 简单高效，STW 明显 | 客户端模式默认 |
| Serial Old | 老年代 | 标记-整理 | 单线程 | CMS 的后备方案 | 在用 |
| ParNew | 新生代 | 复制 | 多线程 | Serial 的多线程版，配合 CMS | JDK 8 常见组合 |
| Parallel Scavenge | 新生代 | 复制 | 多线程 | 吞吐量优先，可自适应调节 | JDK 8 服务端默认 |
| Parallel Old | 老年代 | 标记-整理 | 多线程 | 配合 Parallel Scavenge | 在用 |
| CMS | 老年代 | 标记-清除 | 并发 | 低延迟，有碎片 | JDK 9 废弃，JDK 14 移除 |
| G1 | 整堆 | 复制 + 标记-整理 | 并发 | 可预测停顿，Region 化 | JDK 9+ 默认 |
| ZGC | 整堆 | 并发标记 + 并发转移 | 并发 | 亚毫秒级停顿，TB 级堆 | JDK 11 实验，JDK 15 转正 |
| Shenandoah | 整堆 | 并发标记 + 并发转移 | 并发 | 低延迟，RedHat 主导 | 非 Oracle JDK 常见 |

### CMS（低延迟的经典，必考）

四个阶段：

    1. 初始标记（STW）  ：只标记 GC Roots 直接关联的对象，极快
    2. 并发标记          ：从直接关联对象出发遍历整个对象图，与用户线程并发，最耗时
    3. 重新标记（STW）  ：修正并发标记期间因用户线程继续运行导致的变动（增量更新），比初始标记稍长
    4. 并发清除          ：清除死亡对象，与用户线程并发

缺点（面试常问）：

- **对 CPU 敏感**：并发阶段会占用线程（默认启动 `(CPU 核数 + 3) / 4` 个），核数少时吞吐下降明显；
- **无法处理浮动垃圾**：并发清除期间用户线程新产生的垃圾只能留到下次，因此不能等老年代满了才回收，需要预留空间（-XX:CMSInitiatingOccupancyFraction）；
- **预留空间不够 → Concurrent Mode Failure**，退化为 Serial Old 做一次 Full GC，停顿极长；
- **标记-清除产生碎片**，大对象可能因找不到连续空间而提前触发 Full GC（可用 -XX:+UseCMSCompactAtFullCollection 整理，但会 STW）。

### G1（当前主流）

**核心设计：** 把堆划分成大小相等的 Region（1~32MB，约 2048 个），每个 Region 动态扮演 Eden / Survivor / Old / Humongous，逻辑上仍有分代，物理上不连续。

    ┌────┬────┬────┬────┬────┬────┐
    │ E  │ S  │ O  │ E  │ H  │空闲│
    ├────┼────┼────┼────┼────┼────┤
    │ O  │ E  │ S  │ O  │ E  │ O  │
    └────┴────┴────┴────┴────┴────┘

**回收流程：**

    1. 初始标记（STW）：标记 GC Roots 直接关联对象，修改 TAMS 指针
    2. 并发标记      ：并发遍历对象图，用 SATB 处理漏标
    3. 最终标记（STW）：处理 SATB 记录下来的引用变动
    4. 筛选回收（STW）：计算各 Region 回收价值和成本，按用户期望停顿时间挑选 Region 组成回收集，复制存活对象

**关键技术点：**

- **可预测停顿**：`-XX:MaxGCPauseMillis`（默认 200ms），G1 根据历史数据建模，决定这次只回收哪几个 Region，"智取"而不追求一次清完；
- **记忆集 RSet + 卡表**：解决跨 Region / 跨代引用问题，避免全堆扫描；
- **Humongous**：单个对象超过 Region 一半就放入 Humongous 区，直接算作老年代；
- **两种模式**：Young GC（回收新生代 Region）、Mixed GC（新生代 + 部分老年代）；如果 Mixed GC 跟不上分配速度，会退化为 Full GC（单线程、极慢，必须避免）；
- **JDK 8 需手动开启**（-XX:+UseG1GC），JDK 9 起成为默认。

**回答"为什么 G1 取代 CMS"：** 一是 Region 化 + 按价值回收，能把停顿控制在目标范围内；二是标记-整理性质（复制到新 Region），不会像 CMS 那样产生碎片；三是并发能力更强，堆越大优势越明显。

### ZGC（大内存低延迟）

- **染色指针（Colored Pointers）**：把 GC 信息（标记位、重映射位）直接编码进 64 位指针的高位，对象本身不用改；
- **读屏障（Load Barrier）**：读取引用时判断是否需要修正指针，实现并发转移；
- **并发标记 + 并发转移 + 并发重映射**，STW 阶段只做根节点扫描，停顿与堆大小、存活对象数量基本无关；
- JDK 21 起提供**分代 ZGC**（`-XX:+ZGenerational`），解决了不分代带来的"全堆扫描"问题。

**选型建议：**

    小堆、单机工具 → Serial
    追求吞吐（批处理、离线计算） → Parallel Scavenge + Parallel Old
    追求低延迟、堆 4~32G（互联网服务主流） → G1
    超大堆（>32G）、停顿要求极高（<10ms） → ZGC / Shenandoah

---

## J10. 类加载过程

**一句话结论：** 加载 → 验证 → 准备 → 解析 → 初始化 → 使用 → 卸载，其中验证、准备、解析统称「连接」。

| 阶段 | 做的事 | 考点 |
|---|---|---|
| 加载 | 通过全限定名获取二进制字节流（磁盘、网络、动态生成）→ 转为方法区运行时数据结构 → 在堆中生成 Class 对象 | 数组类不通过类加载器创建，由 JVM 直接生成 |
| 验证 | 文件格式验证、元数据验证、字节码验证、符号引用验证 | 保证字节码不会危害 JVM |
| 准备 | 为**类变量（static）**分配内存并设**零值** | `static int a = 10` 此时 a = 0；但 `static final` 常量会直接赋为 10（ConstantValue 属性） |
| 解析 | 把常量池中的符号引用替换为直接引用 | 可以推迟到首次使用时进行（动态绑定） |
| 初始化 | 执行类构造器 `<clinit>()`，即静态变量赋值和静态代码块 | 父类先于子类初始化；接口不要求父接口先初始化（除非用到） |
| 使用 | 正常使用 | — |
| 卸载 | 类被回收 | 条件极苛刻：该类所有实例已回收、ClassLoader 已回收、Class 对象无引用 |

**六种触发初始化的时机（主动引用）：**

1. `new`、读取或设置类的静态字段（被 final 修饰、已在编译期放入常量池的除外）、调用静态方法；
2. 反射调用（`Class.forName("...")`，注意默认会初始化）；
3. 初始化子类时，父类先初始化；
4. 虚拟机启动时的主类（含 main 方法）；
5. 使用 JDK 7 的动态语言支持（`MethodHandle` 解析结果为 REF_getStatic 等）；
6. 接口中定义了 default 方法，其实现类初始化时接口要先初始化。

**被动引用（不会触发初始化，经典考题）：**

    // 1. 通过子类引用父类的静态字段，只初始化父类
    System.out.println(SubClass.value);   // SubClass 不会初始化

    // 2. 通过数组定义引用类
    SuperClass[] arr = new SuperClass[10];  // 不会初始化 SuperClass

    // 3. 常量在编译期已存入调用方常量池
    System.out.println(ConstClass.HELLO);   // 不会初始化 ConstClass

---

## J11. 类加载器与双亲委派

### 三层类加载器

| 加载器 | 实现语言 | 加载范围 |
|---|---|---|
| Bootstrap ClassLoader | C++ | `JAVA_HOME/lib` 下的核心类（rt.jar / modules） |
| Extension ClassLoader → Platform ClassLoader（JDK 9+） | Java | `JAVA_HOME/lib/ext`，JDK 9 后改为平台类加载器 |
| Application ClassLoader | Java | 用户 classpath |
| 自定义 ClassLoader | Java | 继承 ClassLoader，重写 findClass |

### 双亲委派模型

    Bootstrap ClassLoader
            ↑ 委派
    Extension / Platform ClassLoader
            ↑ 委派
    Application ClassLoader
            ↑ 委派
    自定义 ClassLoader

**加载流程：** 收到加载请求 → 先查自己是否已加载 → 委派给父加载器 → 父加载器再向上委派 → 到 Bootstrap 仍加载不到，才逐层向下尝试自己加载。

**源码（`ClassLoader#loadClass`）：**

    protected Class<?> loadClass(String name, boolean resolve) {
        synchronized (getClassLoadingLock(name)) {
            Class<?> c = findLoadedClass(name);        // 1. 先看自己加载过没
            if (c == null) {
                if (parent != null) {
                    c = parent.loadClass(name, false); // 2. 委派给父加载器
                } else {
                    c = findBootstrapClassOrNull(name); // 3. 父为 null 说明到顶了
                }
                if (c == null) {
                    c = findClass(name);               // 4. 父加载不到才自己加载
                }
            }
            if (resolve) resolveClass(c);
            return c;
        }
    }

**为什么用双亲委派：**

- **避免类重复加载**：父加载器已加载的类，子加载器不会重复加载，保证内存中只有一份；
- **保证核心类库安全**：`java.lang.String` 只能由 Bootstrap 加载，自定义的同名类永远加载不到，防止核心 API 被篡改。

### 打破双亲委派

| 场景 | 做法 | 目的 |
|---|---|---|
| Tomcat | 每个 Web 应用一个 WebAppClassLoader，**先自己加载**，加载不到再委派父类 | 应用之间类隔离，不同应用可用不同版本的同一个库 |
| SPI 机制 | 用 `Thread.currentThread().getContextClassLoader()` 获取线程上下文类加载器 | 让父加载器（Bootstrap）能加载子加载器路径下的实现类，如 JDBC Driver |
| OSGi | 网状委派 | 模块化热部署 |
| 自定义 | 重写 `loadClass` 方法 | 按需定制 |

**SPI 的典型例子：** `DriverManager` 在 rt.jar 里由 Bootstrap 加载，但它要加载各厂商的 Driver 实现（在 classpath 下）。父加载器看不到子加载器的路径，于是通过线程上下文类加载器"反向委派"给子加载器去加载，这就打破了双亲委派的方向。

---

## J12. 调优与排查

### 常用参数

| 参数 | 作用 |
|---|---|
| -Xms / -Xmx | 初始 / 最大堆，生产环境建议设成相等，避免动态扩容引起抖动 |
| -Xss | 单线程栈大小，默认 512K~1M，递归深时调大 |
| -XX:NewRatio | 老年代 : 新生代 |
| -XX:SurvivorRatio | Eden : 单个 Survivor |
| -XX:MaxTenuringThreshold | 晋升年龄阈值 |
| -XX:MetaspaceSize / MaxMetaspaceSize | 元空间初始 / 上限 |
| -XX:+UseG1GC | 指定收集器 |
| -XX:MaxGCPauseMillis | G1 期望的最大停顿时间 |
| -XX:+HeapDumpOnOutOfMemoryError | OOM 时自动 dump 堆 |
| -XX:+PrintGCDetails / -Xlog:gc* | 打印 GC 日志（JDK 9+ 用统一日志） |

### 工具

    jps     查看 Java 进程
    jstat   查看 GC 频率、各代容量与使用率（jstat -gcutil PID 1000）
    jmap    查看堆快照（jmap -dump:format=b,file=heap.hprof PID）
    jstack  查看线程栈，排查死锁和 CPU 飙高
    jinfo   查看和动态修改 JVM 参数
    jcmd    综合命令入口（JDK 7+ 推荐）
    MAT / JProfiler  离线分析 heap dump，看支配树和大对象引用链
    Arthas  线上诊断神器：dashboard、thread、trace、watch、jad

### OOM 排查思路

    1. 提前加 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/path
    2. 用 MAT 打开 dump，看 Leak Suspects 报告和支配树（Dominator Tree）
    3. 找到占用内存最大的对象，看它的 GC Roots 引用链，定位是哪段代码持有
    4. 区分是内存泄漏（该释放没释放）还是单纯配置太小（对象都该活着）
    5. 泄漏 → 修代码；过小 → 调 -Xmx，同时评估是否要扩容或优化数据结构

### CPU 飙高排查（标准五步，必须背熟）

    1. top 找到 CPU 最高的 Java 进程 PID
    2. top -Hp PID 找到该进程内 CPU 最高的线程 TID
    3. printf "%x\n" TID 把线程 ID 转成十六进制
    4. jstack PID > stack.log，在文件里搜这个十六进制 nid
    5. 看该线程的堆栈，定位到具体代码行（可能是死循环、频繁 GC、正则回溯、大量序列化）

如果是 GC 导致的 CPU 飙高，`jstack` 里会看到大量线程停在 GC 相关调用，这时应该用 `jstat -gcutil` 确认，再用 `jmap` dump 分析。

### 内存泄漏常见原因

- 静态集合（`static Map/List`）持续 put 不清理；
- 连接、流、Session 未关闭；
- 监听器、回调注册后未注销；
- `ThreadLocal` 未 remove（线程池复用线程导致 value 长期存活）；
- 自定义缓存没有淘汰策略；
- 非静态内部类持有外部类引用；
- 重写了 `equals` 却没重写 `hashCode`，导致对象放进 Set/Map 后无法命中、无法移除。

---

# 第二部分：Spring

## S1. IoC 与依赖注入

**一句话结论：** IoC 是把对象的创建和依赖管理交给容器，DI 是它最典型的实现手段。

    // 不用 IoC：主动 new，强耦合
    UserService service = new UserService(new UserDaoImpl());

    // 用 IoC：容器创建并注入，只声明依赖
    @Service
    public class UserService {
        private final UserDao userDao;
        public UserService(UserDao userDao) { this.userDao = userDao; }
    }

**容器对比：**

| 容器 | 特点 |
|---|---|
| BeanFactory | 最基础的容器，默认懒加载（getBean 时才创建），功能少、启动快 |
| ApplicationContext | BeanFactory 的超集，默认预加载单例，增加事件发布、国际化、资源加载、AOP 集成 |

**依赖注入的三种方式：**

| 方式 | 优点 | 缺点 | 建议 |
|---|---|---|---|
| 构造器注入 | 依赖不可变（final）、非空、便于单元测试 | 循环依赖无法解决 | **官方推荐** |
| Setter 注入 | 灵活，可解决循环依赖 | 依赖可变，可能为 null | 可选依赖用 |
| 字段注入（@Autowired） | 写法最简洁 | 无法 final、脱离容器难测试、掩盖循环依赖 | 不推荐在核心代码使用 |

**IoC 的好处：** 解耦（依赖面向接口）、统一管理生命周期、便于替换实现和 mock 测试、集中配置。

---

## S2. AOP 面向切面编程

**一句话结论：** AOP 把日志、事务、权限这类横切逻辑从业务代码里抽出来，运行时通过动态代理织入。

### 核心术语

| 术语 | 含义 |
|---|---|
| Aspect | 切面，横切逻辑的模块化（一个类，标注 @Aspect） |
| JoinPoint | 连接点，程序执行过程中可以插入切面的点（Spring 中就是方法调用） |
| Pointcut | 切入点，匹配连接点的表达式（哪些方法要被增强） |
| Advice | 通知，在切面某个连接点上执行的动作 |
| Target | 目标对象，被代理的原始对象 |
| Weaving | 织入，把切面应用到目标对象的过程 |

**五种通知类型：**

    @Before        目标方法执行前
    @AfterReturning 正常返回后（可拿到返回值）
    @AfterThrowing  抛异常后（可拿到异常）
    @After         相当于 finally，无论正常还是异常都执行
    @Around        环绕，最强，可控制是否执行目标方法、修改参数和返回值

**执行顺序（Spring 5.x，同一方法上都有时）：**

    Around 前半段 → Before → 目标方法 → AfterReturning → After → Around 后半段
    （异常时：Around 前半段 → Before → 目标方法抛异常 → AfterThrowing → After）

### 两种动态代理

| 对比 | JDK 动态代理 | CGLIB |
|---|---|---|
| 实现方式 | 基于接口，`Proxy` + `InvocationHandler`，运行时生成实现类 | 基于继承，生成目标类的子类，重写方法 |
| 前提 | 目标类必须实现接口 | 目标类不能是 final，方法不能是 final/private |
| 性能 | 生成快，调用略慢（反射） | 生成慢，调用快（FastClass 索引） |
| Spring 选择 | 有接口默认用 JDK 代理 | 无接口用 CGLIB |

Spring Boot 2.x 起默认 `spring.aop.proxy-target-class=true`，**统一使用 CGLIB**，避免"注入接口正常、注入实现类报错"的坑。

### AOP 应用场景

- **声明式事务**：`@Transactional` 就是基于 AOP 实现的，代理中负责开启、提交、回滚；
- **日志记录**：自定义日志注解，一行代码完成入参出参打印；
- **性能统计**：在目标方法执行前后统计耗时；
- **权限校验**：方法级鉴权、数据权限过滤；
- **缓存**：`@Cacheable` 的读写拦截；
- **分布式锁 / 幂等**：注解 + 切面统一处理。

---

## S3. Bean 生命周期

**一句话结论：** 实例化 → 属性填充 → Aware 回调 → BeanPostProcessor 前置 → 初始化 → BeanPostProcessor 后置（生成 AOP 代理）→ 使用 → 销毁。

    1. 实例化        反射调用构造器创建对象（此时是"原始对象"，字段都是默认值）
    2. 属性填充      依赖注入，@Autowired / @Value 生效
    3. Aware 回调    BeanNameAware、BeanFactoryAware、ApplicationContextAware
    4. BeanPostProcessor#postProcessBeforeInitialization
    5. 初始化        @PostConstruct → InitializingBean#afterPropertiesSet → init-method
    6. BeanPostProcessor#postProcessAfterInitialization  ★ AOP 代理在这里生成
    7. 使用
    8. 销毁          @PreDestroy → DisposableBean#destroy → destroy-method

**面试重点：**

- **AOP 代理在后置处理阶段生成**，所以代理对象是"包装"在原始对象外面的，这也是为什么同类内部调用 `this.method()` 不走代理；
- 初始化方法的三个入口顺序固定：`@PostConstruct` 最先，`afterPropertiesSet` 其次，`init-method` 最后；
- 只有**单例 Bean** 才会被容器完整管理销毁流程，prototype 的销毁容器不负责。

**四种实例化方式：** 构造器（默认）、静态工厂方法、实例工厂方法、FactoryBean 的 `getBean()`。

---

## S4. 循环依赖

**一句话结论：** Spring 用三级缓存解决 Setter/字段注入的循环依赖；构造器注入的循环依赖无法解决。

    A 依赖 B，B 依赖 A

    A 实例化后（还没填充属性）→ 把 A 的对象工厂放入三级缓存
        ↓
    填充 B → 创建 B → B 填充属性时发现需要 A
        ↓
    从三级缓存拿到 A 的工厂 → 生成 A 的早期引用 → 放入二级缓存，删除三级缓存
        ↓
    B 完成初始化 → A 继续填充 B → A 完成

### 三级缓存

| 缓存 | 名称 | 存放内容 |
|---|---|---|
| 一级 | singletonObjects | 完整初始化好的单例 Bean |
| 二级 | earlySingletonObjects | 提前暴露的 Bean（实例化完成、未初始化完成） |
| 三级 | singletonFactories | ObjectFactory 工厂，用于生成早期引用（可能返回代理对象） |

**为什么需要三级而不是两级？**

如果只有二级缓存直接存"早期引用"，那么当 A 需要被 AOP 代理时，早期引用就是原始对象，B 注入的是原始对象而不是代理对象，最终容器里 A 是代理、B 里的 A 是原始对象，两者不一致。

三级缓存存的是**工厂**，只有在真正发生循环依赖、需要提前暴露时，才调用工厂生成（可能已代理的）对象。这样：

- 没有循环依赖的 Bean 永远不会提前调用工厂，符合"正常情况下 AOP 代理在初始化后生成"的语义；
- 有循环依赖时，通过 `getEarlyBeanReference()` 提前生成代理，保证注入的一致性。

**为什么构造器注入解决不了？** 因为构造器注入要求先拿到依赖对象才能 `new`，A 在实例化阶段就卡住了，此时还来不及把任何东西放进三级缓存——Spring 会直接抛 `BeanCurrentlyInCreationException`。

**其他解决方式：**

- 用 `@Lazy` 延迟注入，注入的是代理，真正调用时才解析；
- 改成 Setter / 字段注入；
- 重构：抽公共逻辑到第三个类，消除循环；
- `@DependsOn` 调整初始化顺序（不能解决构造器循环）。

**注意：** Spring Boot 2.6 起默认禁止循环依赖（`spring.main.allow-circular-references=false`），官方态度是"循环依赖本身是设计问题"。

---

## S5. Spring 事务

### 事务失效场景（必背）

| 序号 | 场景 | 原因 |
|---|---|---|
| 1 | 方法非 public | Spring 事务基于 AOP，JDK 代理只能拦截 public 方法 |
| 2 | 同类内部调用 `this.method()` | 不走代理，注解不生效 |
| 3 | 异常被 try-catch 吞掉 | 代理感知不到异常，不会回滚 |
| 4 | 抛的是受检异常 | 默认只对 RuntimeException 和 Error 回滚，需 `rollbackFor = Exception.class` |
| 5 | 数据库引擎不支持事务 | MyISAM |
| 6 | 多线程调用 | 事务绑定在 ThreadLocal 的连接上，不跨线程 |
| 7 | 传播行为配错 | 如 NOT_SUPPORTED、NEVER |
| 8 | 类没被 Spring 管理 | 自己 new 的对象、没加 @Service |
| 9 | 表结构不支持 | DDL 语句会隐式提交，无法回滚 |

**同类调用的三种解法：**

- 拆到不同类（最推荐，符合单一职责）；
- 注入自身代理：`@Autowired private XxxService self;`
- 用 `AopContext.currentProxy()` 调用（需 `@EnableAspectJAutoProxy(exposeProxy = true)`）；
- 用 `TransactionTemplate` 手动控制事务边界，彻底不依赖代理。

### 七种传播行为

| 传播行为 | 含义 | 场景 |
|---|---|---|
| REQUIRED（默认） | 有事务就加入，没有就新建 | 绝大多数情况 |
| REQUIRES_NEW | 挂起当前事务，独立新建一个 | 日志记录、独立提交的子流程 |
| SUPPORTS | 有就加入，没有就以非事务执行 | 查询 |
| NOT_SUPPORTED | 挂起当前事务，以非事务执行 | 不需要事务的耗时操作 |
| MANDATORY | 必须在事务中，否则抛异常 | 强制要求调用方开事务 |
| NEVER | 必须不在事务中，否则抛异常 | 严格校验 |
| NESTED | 嵌套事务，用 savepoint 实现，子事务回滚不影响外层 | 部分失败不影响整体 |

**REQUIRED 与 NESTED 的区别：** REQUIRED 加入外层后是一个整体，任意一方回滚全部回滚；NESTED 用 savepoint，子事务回滚只回滚到保存点，外层可以捕获异常后继续提交。NESTED 只对 DataSourceTransactionManager 有效。

---

## S6. Spring Boot 自动装配

**一句话结论：** `@EnableAutoConfiguration` 导入 `AutoConfigurationImportSelector`，由它读取候选配置类，再通过 `@Conditional` 条件筛选后注册到容器。

    @SpringBootApplication
      = @SpringBootConfiguration（本质是 @Configuration）
      + @EnableAutoConfiguration
      + @ComponentScan（默认扫描主类所在包及子包）

    @EnableAutoConfiguration
      → @Import(AutoConfigurationImportSelector.class)
      → getCandidateConfigurations()
      → 读取 META-INF/spring.factories 中的 EnableAutoConfiguration 键
        （Spring Boot 2.7+/3.x 改用 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports）
      → 去重、排除（exclude / excludeName）
      → 条件过滤：@ConditionalOnClass / @ConditionalOnMissingBean / @ConditionalOnProperty
      → 注册为 BeanDefinition，交给容器实例化

**常用条件注解：**

| 注解 | 作用 |
|---|---|
| @ConditionalOnClass | classpath 存在指定类才生效 |
| @ConditionalOnMissingBean | 容器中没有该 Bean 才生效（**用户自定义优先**的关键） |
| @ConditionalOnProperty | 配置项满足条件才生效（如 `xxx.enabled=true`） |
| @ConditionalOnWebApplication | 是 Web 应用才生效 |
| @ConditionalOnBean | 容器中存在指定 Bean 才生效 |

**自定义 Starter 四步：**

    1. 写属性类：@ConfigurationProperties(prefix = "xxx")
    2. 写自动配置类：@Configuration + @ConditionalOnMissingBean 等条件
    3. 注册：spring.factories（2.7 前）或 AutoConfiguration.imports（2.7+）
    4. 打包发布，使用方引入依赖即可，无需 @ComponentScan

---

## S7. Spring Boot 启动原理

**一句话结论：** `SpringApplication.run()` 做了两件大事——**准备环境**和**刷新容器**，内嵌 Web 服务器在容器 refresh 的 `onRefresh()` 阶段创建并启动。

### 整体流程

    SpringApplication.run(主类.class, args)
        │
        ├── ① 构造 SpringApplication 对象
        │     · 推断应用类型：NONE / SERVLET / REACTIVE（依据 classpath 是否有 WebFlux、Servlet）
        │     · 加载 BootstrapRegistryInitializer、ApplicationContextInitializer、ApplicationListener
        │       （从 spring.factories / .imports 读取）
        │     · 推断主启动类（从调用栈里找 main 方法所在的类）
        │
        └── ② 执行 run() 方法
              1. 启动 StopWatch 计时
              2. 创建 SpringApplicationRunListeners，发布 ApplicationStartingEvent
              3. prepareEnvironment：创建 Environment，加载配置文件、命令行参数、系统变量
                 发布 ApplicationEnvironmentPreparedEvent
              4. printBanner：打印 Banner
              5. createApplicationContext：根据应用类型创建容器
                 （SERVLET → AnnotationConfigServletWebServerApplicationContext）
              6. prepareContext：设置 environment、注册主类 BeanDefinition
                 发布 ApplicationContextInitializedEvent、ApplicationPreparedEvent
              7. refreshContext：调用 AbstractApplicationContext#refresh()  ★核心
              8. afterRefresh：模板方法，默认空实现
              9. stopWatch.stop()，发布 ApplicationStartedEvent
             10. callRunners：依次执行 ApplicationRunner 和 CommandLineRunner
             11. 发布 ApplicationReadyEvent（启动完成，可以对外服务了）

### refresh() 的 12 个步骤（重点看 5、9、11）

| 步骤 | 方法 | 关键动作 |
|---|---|---|
| 1 | prepareRefresh | 记录启动时间、初始化属性源、校验必需属性 |
| 2 | obtainFreshBeanFactory | 创建 DefaultListableBeanFactory |
| 3 | prepareBeanFactory | 设置类加载器、注册内置 BeanPostProcessor（如 ApplicationContextAwareProcessor） |
| 4 | postProcessBeanFactory | 子类扩展，Web 容器在这里注册作用域 |
| 5 | invokeBeanFactoryPostProcessors | **执行 ConfigurationClassPostProcessor，解析 @Configuration/@ComponentScan/@Import，完成自动装配和 BeanDefinition 注册** |
| 6 | registerBeanPostProcessors | 注册 Bean 后置处理器（AOP 的 AnnotationAwareAspectJAutoProxyCreator 就在这里） |
| 7 | initMessageSource | 初始化国际化 |
| 8 | initApplicationEventMulticaster | 初始化事件广播器 |
| 9 | onRefresh | **ServletWebServerApplicationContext 在这里 createWebServer()，创建并启动内嵌 Tomcat** |
| 10 | registerListeners | 注册监听器，发布早期事件 |
| 11 | finishBeanFactoryInitialization | **实例化所有非懒加载的单例 Bean（Bean 生命周期在这里完整走一遍）** |
| 12 | finishRefresh | 发布 ContextRefreshedEvent，启动 LifecycleProcessor，Web 服务器完成启动 |

### 内嵌 Tomcat 是怎么起来的

    ServletWebServerApplicationContext#onRefresh()
        → createWebServer()
        → 从容器拿 ServletWebServerFactory（由 ServletWebServerFactoryAutoConfiguration 提供）
        → TomcatServletWebServerFactory#getWebServer()
        → new Tomcat()、设置端口、创建 Context、注册 DispatcherServlet
        → webServer.start()   ← 到这一步端口才真正被监听

**面试易错点：** Tomcat 的创建比很多人想的要晚——它发生在 `refresh()` 的第 9 步，而**不是** `run()` 一开始。另外端口占用异常的抛出时机也是这里，不是 main 方法刚进来的时候。

### 启动事件顺序

    ApplicationStartingEvent
    ApplicationEnvironmentPreparedEvent
    ApplicationContextInitializedEvent
    ApplicationPreparedEvent
    ContextRefreshedEvent（容器刷新完成）
    ApplicationStartedEvent（2.6 起在 runners 之前发布，之前版本是之后）
    ApplicationReadyEvent（runners 执行完，可以对外提供服务）
    ApplicationFailedEvent（启动失败时）

### ApplicationRunner 与 CommandLineRunner

两者都在**容器刷新完成之后**执行，适合做启动预热（加载缓存、注册到注册中心）：

    @Component
    public class WarmUpRunner implements ApplicationRunner {
        @Override
        public void run(ApplicationArguments args) {
            // args 可以解析 --name=value 形式的参数
        }
    }

    区别：CommandLineRunner 接收原始 String[]，ApplicationRunner 接收已解析的 ApplicationArguments

### 启动耗时优化（进阶追问）

- 延迟初始化：`spring.main.lazy-initialization=true`（代价是首次调用变慢，可能掩盖问题）；
- 排除无用自动配置：`@SpringBootApplication(exclude = ...)`；
- 减少扫描范围：`@ComponentScan` 精确到包，避免扫描 jar；
- 用 Spring Boot 3 的 AOT + GraalVM 原生镜像（启动做到毫秒级）；
- 异步初始化、外部依赖连接超时（数据库、注册中心连不上会把启动拖到几十秒）；
- 用 `--debug` 或 `ApplicationStartup` 打点，先量化再优化。

---

## S8. Spring MVC 请求流程

    ┌──────────────────────────┐
    │     浏览器 / 客户端      │
    └─────────────┬────────────┘
                  │ HTTP 请求
    ┌─────────────▼────────────┐
    │       Filter Chain       │
    └─────────────┬────────────┘
                  │ 编码 / 跨域 / 鉴权
    ┌─────────────▼────────────┐
    │    DispatcherServlet     │
    └─────────────┬────────────┘
                  │ 1. 找处理器
    ┌─────────────▼────────────┐
    │      HandlerMapping      │
    └─────────────┬────────────┘
                  │ 2. 返回 HandlerExecutionChain
    ┌─────────────▼────────────┐
    │      HandlerAdapter      │
    └─────────────┬────────────┘
                  │ 3. 参数解析 + 调用
    ┌─────────────▼────────────┐
    │  Handler（Controller）   │
    └─────────────┬────────────┘
                  │ 4. 处理返回值
    ┌─────────────▼────────────┐
    │   HttpMessageConverter   │
    └─────────────┬────────────┘
                  │ @ResponseBody → JSON
    ┌─────────────▼────────────┐
    │ ViewResolver（非 REST）  │
    └─────────────┬────────────┘
                  │ 5. 渲染视图
    ┌─────────────▼────────────┐
    │        HTTP 响应         │
    └──────────────────────────┘

**核心组件职责：**

| 组件 | 职责 |
|---|---|
| DispatcherServlet | 前端控制器，收口所有请求，编排其余组件 |
| HandlerMapping | URL → Handler 的映射 |
| HandlerAdapter | 真正调用 Handler，屏蔽 Handler 的类型差异 |
| HandlerExceptionResolver | 全局异常处理（@ExceptionHandler、@ControllerAdvice 的落点） |
| ViewResolver | 视图名 → View |
| HttpMessageConverter | HTTP 报文与对象互转（Jackson 在这层） |

**拦截器 vs 过滤器：**

| 对比 | Filter | Interceptor |
|---|---|---|
| 归属 | Servlet 规范 | Spring 框架 |
| 作用范围 | 所有请求（包括静态资源） | 只拦截走 DispatcherServlet 的请求 |
| 执行时机 | 进入 Servlet 之前 | Handler 执行前后 |
| 能否拿到 Bean | 可以（构造注入），但拿不到 Handler 信息 | 可以拿到 HandlerMethod |
| 典型用途 | 编码、跨域、请求包装、XSS 过滤 | 登录鉴权、日志、权限 |

---

## S9. 高频追问速记

| 追问 | 答案要点 |
|---|---|
| 堆和栈的区别 | 堆存对象、共享、GC 管理；栈存栈帧、私有、自动释放 |
| 永久代和元空间的区别 | JDK 8 前在堆内、受 MaxPermSize 限制；之后在本地内存、受 MaxMetaspaceSize 限制 |
| 为什么用元空间替换永久代 | 大小难预估、Full GC 效率低、便于与 JRockit 合并 |
| 对象一定分配在堆上吗 | 不一定：逃逸分析后可栈上分配，TLAB 也在 Eden 内；标量替换还会拆解对象 |
| 为什么新生代用复制算法 | 存活对象极少，复制成本低，且无碎片 |
| 为什么老年代不用复制 | 存活率高，复制成本高，还需要额外一半空间 |
| Minor GC 和 Full GC 区别 | 新生代 vs 整堆 + 方法区；Full GC 慢且要避免频繁 |
| 如何减少 Full GC | 控制对象晋升速度、避免大对象、合理设置新生代大小、选 G1 并设置停顿目标 |
| CMS 和 G1 的区别 | 标记-清除 vs 复制+整理；碎片问题；可预测停顿；Region 化 |
| 三色标记的漏标怎么解决 | 增量更新（CMS）、原始快照 SATB（G1） |
| 类加载什么时候触发 | 六种主动引用：new、反射、子类初始化、主类、MethodHandle、default 方法接口 |
| 双亲委派怎么打破 | Tomcat WebAppClassLoader、SPI 的线程上下文类加载器、OSGi |
| 能不能自定义 java.lang.String | 不能，双亲委派保证核心类只由 Bootstrap 加载，自定义的会被拒绝（Prohibited package name） |
| IoC 和 DI 的关系 | IoC 是思想，DI 是实现手段；容器负责创建和注入 |
| BeanFactory 和 ApplicationContext | 前者懒加载基础容器，后者预加载单例并扩展事件、国际化、AOP |
| AOP 代理什么时候生成 | BeanPostProcessor 的后置处理阶段（postProcessAfterInitialization） |
| JDK 代理和 CGLIB 怎么选 | 有接口用 JDK，无接口用 CGLIB；Spring Boot 2.x 起默认 CGLIB |
| 为什么循环依赖要用三级缓存 | 提前暴露工厂，必要时生成 AOP 代理，保证注入的是代理对象 |
| 构造器循环依赖能解决吗 | 不能，实例化阶段就卡住，直接抛 BeanCurrentlyInCreationException |
| @Transactional 什么时候失效 | 非 public、同类调用、异常被吞、受检异常、多线程、非代理对象 |
| REQUIRED 和 REQUIRES_NEW 区别 | 加入当前事务 vs 挂起当前事务独立新建，前者一起回滚后者独立提交 |
| Spring Boot 自动装配原理 | @EnableAutoConfiguration → @Import(AutoConfigurationImportSelector) → 读候选配置 → @Conditional 过滤 → 注册 BeanDefinition |
| Spring Boot 内嵌 Tomcat 何时启动 | refresh() 的 onRefresh 阶段，由 ServletWebServerApplicationContext 创建并 start |
| Spring Boot 和 Spring 的区别 | 自动装配、内嵌容器、Starter 依赖、约定优于配置、Actuator 监控 |
| @Autowired 和 @Resource 区别 | @Autowired 按类型（配合 @Qualifier 按名称），@Resource 默认按名称 |
| Spring 用了哪些设计模式 | 工厂（BeanFactory）、单例（Bean 默认作用域）、代理（AOP）、模板方法（JdbcTemplate）、观察者（事件机制）、策略（InstantiationStrategy） |

---

## 附：面试表达建议

回答 JVM 与 Spring 问题时，统一用这个结构：

    第一句：给出结论 / 一句话定位
    第二句：讲清机制（分点或按流程）
    第三句：补一个对比或适用场景
    最后：如果被追问，再给参数、源码或实战案例

示例（回答 G1）：

> G1 是 JDK 9 之后的默认收集器，它把堆划分成大小相等的 Region，逻辑上仍分代、物理上不连续。回收时先并发标记，再按各 Region 的回收价值排序，在用户指定的停顿时间目标内挑选收益最高的 Region 做复制回收，所以能做到"可预测停顿"。相比 CMS，它不会产生内存碎片，堆越大优势越明显；缺点是实现复杂，极端情况下仍可能退化为 Full GC。
