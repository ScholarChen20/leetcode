# Java 基础面试八股

> 面试表达建议：先说结论，再说原理、场景和注意事项。每个问题控制在 30 秒到 1 分钟内。

---

## 一、Java 基础与面向对象

### Q1. Java 有什么特点？

**参考答案：** Java 是面向对象、跨平台、自动内存管理并支持并发编程的语言。

- 源码编译为字节码，由 JVM 执行，实现跨平台；
- 支持封装、继承、多态；
- 通过垃圾回收自动管理普通对象内存；
- 不支持类多继承，但支持接口多实现；
- 既有编译过程，也有 JVM 运行时解释和即时编译。

### Q2. 面向对象三大特性是什么？

- **封装：** 隐藏内部实现，通过公开方法提供访问入口；
- **继承：** 子类复用父类属性和方法，表示 is-a 关系；
- **多态：** 父类或接口引用指向不同子类对象，调用同一方法产生不同表现。

### Q3. 重载和重写有什么区别？

| 对比 | 重载 Overload | 重写 Override |
|---|---|---|
| 关系 | 同一个类中 | 父子类之间 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 必须不同 | 必须相同 |
| 返回值 | 不能只靠返回值区分 | 相同或协变返回类型 |
| 权限 | 无特殊限制 | 不能缩小父类方法权限 |
| 决定时机 | 编译期 | 运行期 |

**补充：** private、static、final 方法不能被真正重写；static 方法属于类，通常称为隐藏。

### Q4. 接口和抽象类有什么区别？

| 对比 | 接口 | 抽象类 |
|---|---|---|
| 继承关系 | 一个类可以实现多个接口 | 一个类只能继承一个抽象类 |
| 构造方法 | 没有 | 可以有 |
| 成员变量 | 默认是 public static final | 没有限制 |
| 方法 | 抽象、default、static 等 | 抽象方法和普通方法都可以有 |
| 场景 | 定义能力和行为契约 | 抽取公共状态和实现 |

### Q5. Java 有哪些基本类型？和包装类型有什么区别？

Java 有 8 种基本类型：

- 整数：byte、short、int、long；
- 浮点：float、double；
- 字符：char；
- 布尔：boolean。

| 对比 | 基本类型 | 包装类型 |
|---|---|---|
| 是否对象 | 否 | 是 |
| 泛型支持 | 不支持 | 支持 |
| 默认值 | 例如 int 为 0 | 成员变量通常为 null |
| 比较 | 直接比较值 | == 比较引用，equals 比较内容 |
| 空值 | 不能表示 null | 可以表示 null |

**注意：** 包装类型自动拆箱时可能产生空指针：

    Integer count = null;
    int value = count;

### Q6. == 和 equals 有什么区别？

- 基本类型：== 比较值；
- 引用类型：== 比较是否为同一个对象；
- equals 默认比较引用，String 和包装类等通常重写为比较内容。

    String a = new String("abc");
    String b = new String("abc");

    a == b       // false
    a.equals(b)  // true

### Q7. 局部变量和成员变量有什么区别？

- 局部变量定义在方法、构造器或代码块中，只在局部作用域有效，必须显式初始化；
- 成员变量定义在类中，属于对象或类，有默认值；
- 实例成员通过对象访问，静态成员通过类名访问；
- 局部变量生命周期通常较短，成员变量通常与对象或类相关。

### Q8. 静态方法和实例方法有什么区别？

- 静态方法属于类，可以通过类名调用；
- 实例方法属于对象，需要对象调用；
- 静态方法没有 this，不能直接访问实例成员；
- 实例方法可以访问静态成员和实例成员。

---

## 二、String 相关

### Q9. String、StringBuilder、StringBuffer 有什么区别？

| 类型 | 可变性 | 线程安全 | 适用场景 |
|---|---|---|---|
| String | 不可变 | 是 | 常量、少量拼接 |
| StringBuilder | 可变 | 否 | 单线程大量拼接 |
| StringBuffer | 可变 | 是 | 需要同步的旧场景 |

**结论：** 循环拼接字符串优先使用 StringBuilder。

### Q10. String 为什么不可变？

String 创建后内容不能修改，修改操作会生成新的对象。

优点：

- 可以复用字符串常量池；
- 适合作为 HashMap 的 key，hash 值不会变化；
- 天然线程安全；
- 适合表示路径、权限、类名等不应被修改的内容。

### Q11. 什么是字符串常量池？

字符串常量池用于复用字符串字面量，减少重复对象。

    String a = "abc";
    String b = "abc";
    String c = new String("abc");

    a == b      // true
    a == c      // false
    a.equals(c) // true

### Q12. 为什么重写 equals 必须同时重写 hashCode？

HashMap 和 HashSet 通常先用 hashCode 定位，再用 equals 判断是否相等。

必须满足：

    如果 a.equals(b) 为 true，则 a.hashCode() 必须等于 b.hashCode()

否则可能出现对象逻辑相等，但在集合中查找不到的问题。

---

## 三、Java 集合

### Q13. Java 集合体系如何划分？

    Collection
    ├── List：有序、可重复
    │   ├── ArrayList
    │   └── LinkedList
    ├── Set：通常不允许重复
    │   ├── HashSet
    │   └── TreeSet
    └── Queue / Deque：队列和双端队列

    Map：键值对
    ├── HashMap
    ├── LinkedHashMap
    ├── TreeMap
    └── ConcurrentHashMap

### Q14. ArrayList 和 LinkedList 有什么区别？

| 对比 | ArrayList | LinkedList |
|---|---|---|
| 底层 | 动态数组 | 双向链表 |
| 随机访问 | O(1) | O(n) |
| 中间插入删除 | O(n) | 定位节点后 O(1) |
| 内存局部性 | 好 | 较差 |
| 常用场景 | 查询和遍历多 | 两端操作多 |

**面试结论：** 大多数场景优先 ArrayList；需要频繁两端操作时，通常优先考虑 ArrayDeque。

### Q15. ArrayList 如何扩容？

容量不足时，ArrayList 会创建更大的数组并复制原有元素。扩容会带来复制成本，已知数据量时可以提前设置容量。

    List<User> users = new ArrayList<>(1000);

默认容量和具体扩容比例可能随 JDK 版本变化，重点记住动态数组和扩容复制即可。

### Q16. HashMap 的底层结构是什么？

JDK 8 中，HashMap 底层是数组、链表和红黑树。

    key
      ↓
    计算 hash
      ↓
    定位桶
      ↓
    equals 比较
      ↓
    查询或插入

桶中节点过多时可能树化，降低极端情况下的查询退化。

### Q17. HashMap 的 put 流程是什么？

1. 计算 key 的 hash；
2. 根据 hash 定位数组下标；
3. 桶为空，直接创建节点；
4. key 已存在，覆盖 value；
5. key 不存在，加入链表或红黑树；
6. 元素超过阈值，扩容。

### Q18. HashMap 为什么容量通常是 2 的幂？

容量为 2 的幂时，可以用位运算快速计算桶下标：

    (n - 1) & hash

相比取模运算效率更高，也有利于 hash 值均匀分布，减少冲突。

### Q19. HashMap 的负载因子是什么？

    负载因子 = 元素数量 / 数组容量

超过容量乘以负载因子后会扩容。默认值通常是 0.75，是空间利用率和查询性能之间的折中。

### Q20. HashMap 为什么线程不安全？

HashMap 没有并发保护。多个线程同时 put、扩容或修改同一桶时，可能出现：

- 数据覆盖或丢失；
- size 不准确；
- 读取到不一致的数据。

并发场景使用 ConcurrentHashMap 或外部锁。

### Q21. HashMap、Hashtable、ConcurrentHashMap 有什么区别？

| 类型 | 线程安全 | 并发性能 | null 支持 |
|---|---|---|---|
| HashMap | 否 | 高 | 允许 null key 和 null value |
| Hashtable | 是 | 较低，方法级同步 | 不允许 null |
| ConcurrentHashMap | 是 | 较高 | 不允许 null |

**结论：** 新代码并发场景优先使用 ConcurrentHashMap，不建议使用 Hashtable。

### Q22. HashSet 如何保证元素不重复？

HashSet 底层通常基于 HashMap，元素作为 key 保存。添加时先比较 hash，再通过 equals 判断是否重复。

自定义对象放入 HashSet 时，必须正确重写 equals 和 hashCode。

### Q23. TreeMap 和 HashMap 有什么区别？

- HashMap 基于哈希表，平均查询接近 O(1)，不保证顺序；
- TreeMap 基于红黑树，key 有序，查询、插入、删除通常为 O(logN)；
- 快速查找用 HashMap，需要排序或范围查询用 TreeMap。

### Q24. LinkedHashMap 有什么特点？

LinkedHashMap 在 HashMap 基础上维护双向链表，可以保持插入顺序，也可以配置为访问顺序。

常见用途：

- 保持遍历顺序；
- 实现简单 LRU 缓存；
- 按访问顺序淘汰数据。

### Q25. 什么是 fail-fast？

遍历集合时，如果检测到集合被非迭代器方式结构性修改，可能抛出 ConcurrentModificationException。

安全方式：

- 使用迭代器的 remove；
- 使用并发容器；
- 先收集待删除元素，再统一删除。

fail-fast 是错误检测机制，不是线程安全保证。

### Q26. CopyOnWriteArrayList 适合什么场景？

它采用写时复制，适合读多写少的场景，如监听器、配置快照和订阅列表。

- 优点：读操作通常不加锁，迭代器具有快照语义；
- 缺点：写操作复制数组，内存和性能成本较高；
- 不适合频繁写入。

### Q27. PriorityQueue 是什么？

PriorityQueue 基于堆实现，默认是小根堆，每次取出最小元素。

- 查看堆顶：O(1)；
- 插入、删除堆顶：通常 O(logN)；
- 不保证整体遍历结果有序。

---

## 四、异常体系

### Q28. Java 异常如何分类？

    Throwable
    ├── Error：JVM 或系统级错误，通常不处理
    └── Exception
        ├── RuntimeException：运行时异常，通常是代码问题
        └── Checked Exception：受检异常，必须捕获或声明抛出

示例：

- Error：OutOfMemoryError、StackOverflowError；
- 运行时异常：NullPointerException、数组越界；
- 受检异常：IOException、SQLException。

### Q29. finally 和 return 的执行顺序是什么？

- 正常情况下 finally 会执行；
- System.exit 或 JVM 崩溃时可能不执行；
- finally 中的 return 会覆盖 try/catch 中的 return，不建议这样写；
- return 表达式通常先计算，再执行 finally。

---

## 五、泛型

### Q30. 什么是 Java 泛型？

泛型在编译期提供类型检查，减少强制类型转换，提高代码复用性。

    List<String> names = new ArrayList<>();

泛型可以用于类、接口和方法。泛型参数不能使用基本类型，只能使用包装类型。

### Q31. 什么是泛型擦除？

Java 泛型主要是编译期特性，编译后类型参数会被擦除并替换为上界，默认是 Object。

影响：

- 不能直接 new T；
- 不能使用 instanceof List<String>；
- 不能直接创建泛型数组；
- List<String> 和 List<Integer> 运行时通常是同一个类。

### Q32. extends 和 super 有什么区别？

| 写法 | 含义 | 读取 | 写入 |
|---|---|---|---|
| ? extends T | T 或 T 的子类 | 可以按 T 读取 | 不能安全写入具体对象 |
| ? super T | T 或 T 的父类 | 只能按 Object 读取 | 可以写入 T |

口诀：

    PECS：Producer Extends，Consumer Super

---

## 六、反射与动态代理

### Q33. 什么是反射？有什么应用？

反射是在运行时获取类信息并操作对象、方法和字段的机制。

获取 Class 对象的方式：

    Class.forName("com.example.User");
    User.class;
    user.getClass();

常见应用：

- Spring IoC 创建和管理 Bean；
- ORM 框架映射对象和数据库；
- 注解处理；
- 动态代理。

缺点是运行时开销较高、破坏封装，类型安全较弱。

### Q34. 什么是动态代理？AOP 中如何使用？

**一句话结论：** 动态代理通过拦截方法调用，在不修改业务代码的情况下织入日志、事务、权限等横切逻辑。

    调用代理对象
        ↓
    权限校验 / 日志 / 开启事务
        ↓
    调用目标业务方法
        ↓
    提交事务 / 后置处理

- JDK 动态代理：目标类必须实现接口；
- CGLIB：生成目标类的子类，目标类不要求实现接口；
- Spring AOP 会根据情况选择代理方式。

---

## 七、Java 并发

### Q35. 进程和线程有什么区别？

- 进程是资源分配的基本单位，拥有独立地址空间；
- 线程是 CPU 调度的基本单位；
- 同一进程中的线程共享堆和方法区；
- 线程通常拥有独立的栈和程序计数器；
- 进程隔离性更强，线程创建和切换成本更低。



### Q36. Java 并发/并行区别，并发的三大特性是什么？
并发：两个及两个以上的作业在同一 时间段 内执行。
并行：两个及两个以上的作业在同一 时刻 执行。
- **原子性：** 操作不可被打断；
- **可见性：** 一个线程的修改能被其他线程看到；
- **有序性：** 执行结果符合代码逻辑，避免重排序问题。

### Q37. synchronized 的作用是什么？

synchronized 保证同一时刻只有一个线程进入临界区，并保证锁释放前的修改对后续获得同一把锁的线程可见。

- 实例方法锁当前对象；
- 静态方法锁对应的 Class 对象；
- 同步代码块锁括号中的对象；
- synchronized 是可重入锁；
- 异常退出时 JVM 会自动释放锁。

### Q37.1. synchronized 的底层原理是什么？

**参考答案：** synchronized 的底层依赖 JVM 的监视器锁（Monitor），用对象头里的 Mark Word 记录锁状态，最终由操作系统的互斥量（mutex）保证互斥。

先看字节码层面：

- 同步代码块：编译后生成 `monitorenter` 和 `monitorexit` 指令，而且通常有两个 `monitorexit`（正常路径一个、异常路径一个），保证抛异常时也能释放锁；
- 同步方法：方法访问标志位 `ACC_SYNCHRONIZED`，调用时由 JVM 隐式加锁解锁，不需要指令。

再看对象与 Monitor 的关系：

    对象头 Mark Word  →  指向 ObjectMonitor
    ObjectMonitor
    ├── _owner      ：当前持有锁的线程
    ├── _recursions ：重入次数
    ├── _EntryList  ：竞争锁失败、阻塞等待的线程
    └── _WaitSet    ：调用 wait() 后挂起的线程

**可重入的实现：** 线程再次进入同步块时，先判断 `_owner` 是不是自己，是则 `_recursions + 1`；退出时减 1，减到 0 才真正释放锁。

**面试结论：** 按「字节码 → 对象头 Mark Word → ObjectMonitor → 操作系统 mutex」逐层往下说，是最容易被认可的答法。注意说清楚：重量级锁才有真正的 Monitor 膨胀，轻量级锁阶段还没走到这一步。

### Q37.2. synchronized 的锁升级过程是怎样的？

JDK 6 之后为了减少无谓的内核态切换，引入了锁升级：无锁 → 偏向锁 → 轻量级锁 → 重量级锁，通常只能升级不能降级。

| 锁状态 | Mark Word 记录内容 | 加锁方式 | 适用场景 |
|---|---|---|---|
| 无锁 | hash、分代年龄，锁标志 01 | 无 | 无线程竞争 |
| 偏向锁 | 线程 ID + epoch，标志 01 | 首次 CAS 记录线程 ID，同一线程后续直接进入 | 始终只有一个线程访问 |
| 轻量级锁 | 指向栈帧中 Lock Record 的指针，标志 00 | CAS 替换 Mark Word，失败则自旋 | 线程交替执行，竞争时间极短 |
| 重量级锁 | 指向 ObjectMonitor 的指针，标志 10 | 进入 EntryList 阻塞，涉及用户态/内核态切换 | 竞争激烈、临界区执行时间长 |

几个容易踩的点：

- **偏向锁已被废弃。** JDK 15 起默认关闭（JEP 374），JDK 18 正式移除。原因是撤销偏向锁需要 STW，而现代应用大量使用并发容器，偏向锁命中率低、维护成本高。被问到就说"知道它存在、知道为什么被移除"，不要当成现役机制讲。
- **轻量级锁适合"交替"而不是"同时"。** 它的本质是用 CAS 加自旋代替阻塞，两个线程真正同时抢同一把锁时会很快膨胀。
- **自旋失败才膨胀。** 自适应自旋仍然失败后，才把 Mark Word 改成指向 ObjectMonitor，线程进入内核态挂起。

**面试结论：** 锁升级的核心目的是"无竞争或轻竞争时尽量待在用户态"，用 CAS 和自旋换取性能；只有真打起来才退化成操作系统互斥量。

### Q37.3. synchronized 有哪些锁优化手段？

- **自旋锁：** 竞争时不立刻阻塞，而是循环重试一小段时间，避免线程切换开销；
- **自适应自旋：** 自旋次数不固定，由上一次在同一把锁上的成功率动态决定，JVM 会"学习"；
- **锁消除：** JIT 通过逃逸分析发现锁对象不会逃逸出当前线程（例如方法内 new 的局部 StringBuilder），直接把同步去掉；
- **锁粗化：** 把循环内多次连续的加锁解锁合并成一次大的加锁，减少反复申请释放的开销。

### Q38. synchronized 和 ReentrantLock 有什么区别？

| 对比 | synchronized | ReentrantLock |
|---|---|---|
| 类型 | 关键字 | JDK 类 |
| 释放锁 | 自动 | 手动 unlock |
| 超时获取 | 不支持 | 支持 tryLock |
| 可中断获取 | 不直接支持 | 支持 |
| 公平锁 | 不方便配置 | 支持 |
| 条件队列 | 一个隐含条件队列 | 可创建多个 Condition |

使用 ReentrantLock 时，必须在 finally 中释放锁。

### Q38.1. AQS 的原理是什么？

**参考答案：** AQS（AbstractQueuedSynchronizer）用「一个 volatile int 状态位 + 一个双向等待队列」实现了锁和同步器，ReentrantLock、Semaphore、CountDownLatch 都建立在它之上。

    volatile int state   ← 用 CAS 修改表示同步状态
          │
          ▼
    CLH 变体双向队列
    head → Node(thread) ⇄ Node(thread) ⇄ Node(thread) ← tail

- **state 的含义由子类决定：** ReentrantLock 中表示重入次数；Semaphore 中表示可用许可数；CountDownLatch 中表示未完成的计数；
- **获取失败的线程入队：** 包装成 Node 加入队尾，然后 `LockSupport.park()` 挂起；
- **释放时唤醒后继：** `unpark` 队列中下一个有效节点；
- **模板方法模式：** AQS 只定义排队和阻塞的骨架，留出 `tryAcquire` / `tryRelease` 给子类实现；
- **公平与非公平：** 公平锁在 `tryAcquire` 里先判断队列前面有没有人排队，非公平锁直接抢（可能插队），因此非公平锁吞吐更高。

**面试结论：** 一句话概括——AQS 把"抢不到资源怎么办"（排队 + 挂起 + 唤醒）这套通用逻辑抽出来，子类只需要定义"什么算抢到"。

### Q39. volatile 有什么作用？

**参考答案：** volatile 保证共享变量的可见性和有序性（禁止指令重排序），但不保证原子性。

三个语义分别对应：

- **可见性：** 写操作立即刷回主内存，并让其他线程中该变量的缓存行失效；读操作会重新从主内存加载，因此能读到最新值；
- **有序性：** 通过内存屏障禁止 volatile 读写与前后指令发生重排序；
- **不保证原子性：** `count++` 是读、改、写三步，多线程下依然会丢失更新。

适合的场景：

    // 1. 状态标记位
    private volatile boolean running = true;

    // 2. DCL 单例的实例引用
    private volatile Singleton instance;

    // 3. 一写多读的配置、开关、事件通知标志

不适合的场景：

- 计数、累加类复合操作 → 用 AtomicInteger、LongAdder 或锁；
- 多个变量之间需要保持一致 → 用锁，volatile 只能保证单个变量的可见性。

### Q39.1. volatile 的底层是如何实现的？

**参考答案：** 从字节码到硬件一共三层，答题按这个顺序说最稳。

1. **字节码层：** 字段访问标志加 `ACC_VOLATILE`，JVM 看到这个标志就知道要特殊处理；
2. **JVM 层：** 按 JMM 规范在 volatile 写前后插入 `StoreStore` + `StoreLoad` 屏障，在读前后插入 `LoadLoad` + `LoadStore` 屏障，禁止跨屏障重排序；
3. **硬件层：** x86 上 volatile 写最终编译成带 `lock` 前缀的指令（如 `lock addl $0x0,(%rsp)`），`lock` 前缀做了三件事：
   - 把当前 CPU 缓存行立即写回主内存；
   - 基于缓存一致性协议（MESI）让其他 CPU 中该缓存行失效；
   - 充当内存屏障，阻止指令重排。

**追问准备：** volatile 变量本身是原子的（JLS 保证包括 long/double 在内的 volatile 读写原子），但"读 + 改 + 写"这一串不是原子的，这两件事不要混为一谈。

### Q39.2. 什么是 JMM 和 happens-before？

**参考答案：** JMM（Java 内存模型）是 JVM 定义的一套并发语义规范，它把内存抽象成主内存（所有线程共享）和 工作内存（每个线程私有，可以理解为 CPU 缓存和寄存器的抽象），并规定线程只能通过这八个原子操作交互：

    lock / unlock   read / load   use / assign   store / write

happens-before 是判断"一个操作的结果是否对另一个操作可见"的依据，主要规则：

- **程序顺序规则：** 同一线程内，前面的操作 happens-before 后面的操作；
- **监视器锁规则：** 对同一把锁的 unlock happens-before 后续的 lock；
- **volatile 规则：** 对 volatile 变量的写 happens-before 后续对该变量的读；
- **线程启动规则：** `Thread.start()` happens-before 子线程中的任何操作；
- **线程终止规则：** 线程内所有操作 happens-before 其他线程从 `join()` 返回；
- **传递性：** A hb B，B hb C，则 A hb C。

**注意：** happens-before 不等于"时间上先发生"，它是可见性约束。两条指令在时间上没顺序，也可能存在 happens-before 关系。

### Q39.3. 为什么 DCL 单例必须加 volatile？

这是 volatile 在业务代码里最高频的考点。

    public class Singleton {
        private static volatile Singleton instance;   // 少了 volatile 就是错的

        public static Singleton getInstance() {
            if (instance == null) {                  // 第一次检查
                synchronized (Singleton.class) {
                    if (instance == null) {          // 第二次检查
                        instance = new Singleton();  // ① 问题在这里
                    }
                }
            }
            return instance;
        }
    }

① 这一行在字节码层面是三步：

    1. 分配内存空间
    2. 调用构造器初始化对象
    3. 把引用赋值给 instance

没有 volatile 时，JIT 或 CPU 可能把第 3 步重排到第 2 步之前。此时另一个线程走到外层 `if (instance == null)`，发现不为 null 就直接返回，拿到的是一个"内存已分配但还没初始化完"的半成品对象，后续使用可能空指针或读到默认值。

volatile 的作用就是禁止这个重排序。

**面试结论：** 一句话——volatile 在这里不是为了可见性，而是为了禁止 `new` 过程中的指令重排。

### Q39.4. volatile 和 synchronized 有什么区别？

| 对比 | volatile | synchronized |
|---|---|---|
| 原子性 | 不保证复合操作 | 保证临界区整体原子 |
| 可见性 | 保证 | 保证（解锁前刷新、加锁后重读） |
| 有序性 | 禁止指令重排 | 保证临界区内代码的原子与有序 |
| 是否阻塞 | 不阻塞 | 会阻塞、可能涉及内核态切换 |
| 作用粒度 | 单个变量 | 代码块或方法 |
| 典型场景 | 状态标记、DCL | 复合操作、多变量一致性 |

**面试结论：** volatile 是"轻量级的同步"，解决的是可见性和重排，不是互斥；需要互斥时必须用锁。

### Q40. 什么是 CAS？有什么问题？

**参考答案：** CAS（Compare And Swap）是比较并交换：比较内存中的当前值是否等于预期值，相等则更新为新值，否则放弃并重试。整个"比较 + 更新"由 CPU 一条指令完成，是原子的。

Java 中的入口是 `Unsafe.compareAndSwapInt` 等方法，底层对应 x86 的 `cmpxchg` 指令（配合 `lock` 前缀保证多核原子性），JDK 9 之后更推荐用 `VarHandle` 替代 Unsafe。

    当前值 == 预期值 ?
        ├── 是 → 写入新值，返回成功
        └── 否 → 不做任何修改，返回失败（通常外层自旋重试）

优点：非阻塞、无锁竞争时开销极小，适合简单的原子更新。

问题（面试必背四点）：

- **自旋开销：** 高竞争下大量线程 CAS 失败反复重试，空耗 CPU；
- **只能保证单个变量原子性：** 多个变量要一起改，只能封装成对象用 `AtomicReference`，或者直接加锁；
- **ABA 问题：** 值被改走又改回来，CAS 察觉不到中间变化；
- **公平性差：** 谁抢到算谁的，可能出现线程饥饿，也不保证顺序。

### Q40.1. AtomicInteger 是怎么用 CAS 实现原子自增的？

核心是「volatile value + 字段偏移量 + CAS 自旋」：

    public final int getAndIncrement() {
        return unsafe.getAndAddInt(this, valueOffset, 1);
    }

    // Unsafe#getAndAddInt 的真实写法（JDK 8）
    public final int getAndAddInt(Object o, long offset, int delta) {
        int v;
        do {
            v = getIntVolatile(o, offset);                            // 读当前值
        } while (!compareAndSwapInt(o, offset, v, v + delta));        // 失败就重读重试
        return v;
    }

- `valueOffset` 是 value 字段在对象内存中的偏移量，通过反射在静态代码块里取得；
- value 本身用 volatile 修饰，保证读到的是最新值，CAS 才能基于正确预期值比较；
- 失败重试而不是阻塞，这就是所谓的"无锁 / 自旋"。

### Q40.2. 什么是 ABA 问题？如何解决？

线程 1 读到 A；线程 2 把 A 改成 B，又改回 A；线程 1 的 CAS 依然成功，但它并不知道中间已经变过。

单纯的数值替换场景通常无害，但**依赖对象状态**的场景就有风险，比如链表节点被回收后复用、栈顶引用、账户状态流转。

解决方式：

| 方案 | 做法 | 特点 |
|---|---|---|
| AtomicStampedReference | 比较「引用 + 版本号 stamp」两部分 | 最常用，能识别"改过又改回" |
| AtomicMarkableReference | 只加一个 boolean 标记 | 只关心"是否被改过"，不关心改了几次 |
| 加锁 | 直接互斥 | 最简单，但放弃无锁收益 |

### Q40.3. AtomicLong 和 LongAdder 有什么区别？

| 对比 | AtomicLong | LongAdder |
|---|---|---|
| 结构 | 单个 volatile value | base + Cell 数组 |
| 高并发写 | 所有线程 CAS 同一个值，冲突高 | 分散到不同 Cell，冲突大幅降低 |
| 读取 | 直接读，强一致 | `sum()` 汇总各 Cell，弱一致 |
| 内存占用 | 小 | 更大（空间换时间） |
| 适用场景 | 需要精确读取、竞争不激烈 | 高并发统计计数、监控埋点 |

**面试结论：** LongAdder 本质是分段思想——把热点打散到多个 Cell，最后再汇总，和 ConcurrentHashMap 的分段锁思路一脉相承。代价是 `sum()` 期间可能读到不一致的中间结果。

### Q40.4. 什么是乐观锁和悲观锁？

- **悲观锁：** 认为并发冲突一定会发生，操作前先加锁，其他线程阻塞等待；
- **乐观锁：** 认为冲突较少，不加锁直接操作，提交时再校验数据有没有被别人改过，冲突则失败重试。

| 对比 | 悲观锁 | 乐观锁 |
|---|---|---|
| 核心思想 | 先加锁，再操作 | 先操作，提交时校验 |
| 是否阻塞 | 是，抢不到就等 | 否，失败重试 |
| 开销来源 | 加锁、线程切换、内核态开销 | 无锁开销，冲突时重试成本 |
| 适用场景 | 写多、冲突多、临界区较长 | 读多写少、冲突少 |
| Java 体现 | synchronized、ReentrantLock | CAS、AtomicInteger |
| 数据库体现 | `select ... for update`、InnoDB 行锁 | version 字段 + where 条件校验 |

**选型口诀：** 冲突少用乐观锁，冲突多用悲观锁；读多写少用乐观锁，长事务和强一致用悲观锁。

**注意：** 严格说 Java 里的 CAS 是"无锁"，数据库里的 version 才是教科书式乐观锁，两者是实现手段和思想的关系，面试时讲清这层区别会加分。

### Q40.5. 数据库乐观锁怎么写？有哪些坑？

标准写法是用 version 字段做条件校验：

    -- 1. 先查询，拿到当前版本号
    select id, stock, version from goods where id = 1;

    -- 2. 更新时把版本号作为条件，同时递增
    update goods set stock = stock - 1, version = version + 1
    where id = 1 and version = 5;

然后判断 `update` 的影响行数：返回 1 表示成功，返回 0 表示期间被别人改过，需要重试或提示用户。

几个坑：

- **重试必须有上限。** 高冲突下会疯狂失败，通常重试 2~3 次后直接失败，避免拖垮数据库；
- **业务字段和 version 必须在同一条 update 里。** 否则中间状态可能被其他事务读到；
- **乐观锁只保证更新不覆盖别人的修改，不保证读到的数据是最新的。** 业务判断如果依赖"读到的旧值"，仍需加锁或改用当前读；
- **高冲突场景应该换悲观锁。** 重试率飙升时，乐观锁的性能优势会反转。

对比一下悲观锁的写法与风险：

    -- 悲观锁：一定要走索引，否则 InnoDB 可能锁表而不是锁行
    select * from goods where id = 1 for update;

**面试结论：** 乐观锁 = 版本号 + 条件更新 + 影响行数判断 + 有限重试。答完这四步，再补一句"高冲突场景不适合"，就是完整答案。

### Q41. 什么是线程池？为什么使用线程池？

线程池复用线程执行任务，避免频繁创建和销毁线程，同时控制并发数量。

主要作用：

- 降低线程创建开销；
- 控制系统并发度；
- 支持任务排队和拒绝策略；
- 统一管理线程和任务。

生产环境通常直接使用 ThreadPoolExecutor，避免无脑使用 Executors。

### Q42. ThreadPoolExecutor 的核心参数有哪些？

- corePoolSize：核心线程数；
- maximumPoolSize：最大线程数；
- keepAliveTime：非核心线程空闲存活时间；
- workQueue：任务队列；
- threadFactory：线程创建工厂；
- RejectedExecutionHandler：拒绝策略。

任务处理顺序：

    创建核心线程 → 进入队列 → 创建非核心线程 → 执行拒绝策略

### Q43. 线程池有哪些拒绝策略？

- AbortPolicy：抛出异常，默认策略；
- CallerRunsPolicy：提交任务的线程执行；
- DiscardPolicy：直接丢弃；
- DiscardOldestPolicy：丢弃队列中最旧的任务，再尝试提交。


### Q43.1. 线程池常用的阻塞队列有哪些？

**参考答案：**

| 队列 | 特点 | 常见场景 |
|---|---|---|
| ArrayBlockingQueue | 有界数组队列，容量固定 | 控制任务堆积，常用于生产环境 |
| LinkedBlockingQueue | 链表队列，可有界或近似无界 | 吞吐较好，但要注意队列过大 |
| SynchronousQueue | 不存储任务，直接交给线程 | 快速提交和线程扩容 |
| PriorityBlockingQueue | 按优先级取任务，通常无界 | 优先级任务调度 |
| DelayQueue | 元素到期后才能取出 | 延迟任务、定时任务 |

阻塞队列满时，生产者可能等待；队列为空时，消费者可能等待。队列选择会直接影响吞吐、延迟和内存风险。

### Q43.2. Executors 返回线程池对象有什么弊端？

**参考答案：**

不建议直接使用 Executors 创建线程池，因为默认参数可能导致资源失控：

- newFixedThreadPool 和 newSingleThreadExecutor 使用近似无界的 LinkedBlockingQueue，任务堆积可能导致 OOM；
- newCachedThreadPool 使用 SynchronousQueue，线程数几乎无界，突发任务可能创建大量线程；
- newScheduledThreadPool 也可能积累大量延迟任务，缺少业务级容量控制。

**推荐做法：** 直接使用 ThreadPoolExecutor，明确设置核心线程数、最大线程数、队列容量、线程工厂和拒绝策略。

### Q44. 线程池线程数如何设置？

- CPU 密集型：通常接近 CPU 核数；
- I/O 密集型：可以大于 CPU 核数；
- 混合任务：最好拆分到不同线程池；
- 最终需要结合任务耗时、队列大小和下游承载能力压测确定。

### Q45. CountDownLatch、CyclicBarrier、Semaphore 有什么区别？

| 工具 | 作用 |
|---|---|
| CountDownLatch | 一个或少数线程等待多个任务完成，一次性 |
| CyclicBarrier | 多个线程互相等待到达同一阶段，可重复使用 |
| Semaphore | 限制同时访问资源的线程数量 |

### Q46. wait、notify 和 sleep 有什么区别？

| 方法 | 是否释放锁 | 说明 |
|---|---|---|
| wait | 是 | 必须持有对象锁，等待条件 |
| notify | 不立即释放 | 唤醒一个等待线程 |
| notifyAll | 不立即释放 | 唤醒所有等待线程 |
| sleep | 否 | 休眠指定时间 |

### Q47. 什么是死锁？如何避免？

死锁是多个线程互相等待对方持有的锁，导致线程都无法继续执行。

四个必要条件：

    互斥、占有并等待、不可剥夺、循环等待

避免方式：

- 按固定顺序获取锁；
- 缩小锁范围；
- 避免嵌套锁；
- 使用 tryLock 超时；
- 在 finally 中释放锁。

### Q48. 什么是 ThreadLocal？

ThreadLocal 为每个线程保存独立副本，适合保存用户上下文、请求上下文和事务上下文。

**注意：** 在线程池中使用后要及时 remove，避免线程复用导致数据串用和内存泄漏。


### Q48.1. ThreadLocal 的底层原理是什么？

**参考答案：**

每个线程内部都有一个 ThreadLocalMap，ThreadLocal 作为 key，线程自己的变量作为 value：

    Thread
      └── ThreadLocalMap
            └── Entry(ThreadLocal -> value)

调用 set/get 时，ThreadLocal 先获取当前线程，再操作当前线程的 ThreadLocalMap，因此不同线程之间互不影响。

ThreadLocalMap 的 Entry 对 ThreadLocal 使用弱引用，但 value 仍可能是强引用。

### Q48.2. ThreadLocal 为什么可能发生内存泄漏？

**参考答案：**

当 ThreadLocal 对象没有外部强引用时，Entry 的 key 可能被 GC 回收，但 value 仍然存在于线程的 ThreadLocalMap 中：

    key = null，value 仍被 ThreadLocalMap 引用

如果线程是线程池中的长期复用线程，value 可能长期无法释放，还可能造成数据残留和内存泄漏。

**解决方式：**

- 使用完 ThreadLocal 后主动调用 remove；
- 在线程池任务的 finally 中清理；
- 不要把大对象或生命周期很长的对象长期放入 ThreadLocal。

### Q48.3. 如何跨线程传递 ThreadLocal 的值？

**参考答案：**

普通 ThreadLocal 的值不会自动传递到子线程，因为每个线程都有独立的 ThreadLocalMap。

常见方案：

- InheritableThreadLocal：创建子线程时复制父线程值，但不适合线程池，因为线程复用时不会每次重新复制；
- TransmittableThreadLocal：配合 TTL 等工具，在任务提交和执行时传递上下文，适合线程池；
- 手动把上下文作为任务参数传递：最明确，也最容易控制生命周期。

**面试结论：** 跨线程传递用户信息、链路追踪等上下文时，要注意线程池复用导致的上下文污染，任务结束后及时清理。

### Q49. CompletableFuture 有什么作用？

CompletableFuture 用于异步任务编排，可以处理任务依赖、结果转换、任务组合和异常。

    CompletableFuture
            .supplyAsync(() -> "hello")
            .thenApply(String::toUpperCase)
            .thenAccept(System.out::println);

常用方法：

- thenApply：转换结果；
- thenAccept：消费结果；
- thenCombine：组合两个任务；
- allOf：等待多个任务；
- exceptionally：处理异常。

线程池中线程异常后，销毁还是复用？
使用 execute() 时，未捕获异常导致线程终止，线程池创建新线程替代；使用 submit() 时，异常被封装在 Future 中，线程继续复用。

---

## 八、JDK 8 常用特性

### Q50. Lambda 和函数式接口是什么？

Lambda 是函数式接口的简洁实现。函数式接口只有一个抽象方法。

常用接口：

- Function：输入并转换；
- Predicate：判断；
- Consumer：消费；
- Supplier：提供结果。

### Q51. Stream 的特点是什么？

Stream 用于对集合进行声明式处理。

- 中间操作：filter、map、sorted、distinct；
- 终止操作：collect、forEach、count；
- 中间操作是惰性的，遇到终止操作才执行；
- Stream 不负责存储数据，不能简单等同于集合。

### Q52. Optional 有什么作用？

Optional 用于表达值可能为空，减少直接判空导致的 NPE。

    String name = Optional.ofNullable(user)
            .map(User::getName)
            .orElse("未知");

适合返回值和链式转换，不建议滥用于实体字段和所有方法参数。

---

## 九、IO 与序列化

### Q53. BIO、NIO、AIO 有什么区别？

| 模型 | 特点 | 典型场景 |
|---|---|---|
| BIO | 阻塞，一个连接通常占一个线程 | 连接数少、模型简单 |
| NIO | 非阻塞，多路复用 | 高并发网络服务 |
| AIO | 异步完成通知 | 特定异步 IO 场景 |

Netty 主要基于 NIO 和 Reactor 模型。

### Q54. 什么是序列化和反序列化？

- 序列化：对象转换为可存储或传输的数据；
- 反序列化：数据还原为对象。

常见方案：

- Java 原生序列化：注意 Serializable 和 serialVersionUID；
- JSON：可读、跨语言；
- Protobuf：体积小、性能好，常用于 RPC；
- Kryo：Java 场景下性能较高。

---

## 十、高频追问速记

| 问题 | 直接回答 |
|---|---|
| String 为什么不可变？ | 便于常量池复用、作为 HashMap key、线程安全和安全性 |
| Integer 缓存范围？ | 默认缓存 -128 到 127，具体范围可配置 |
| Integer 用 == 有什么坑？ | 缓存范围内可能相等，超出范围通常是不同对象，应使用 equals |
| HashMap 为什么用红黑树？ | 链表过长时，将查询从 O(n) 降到 O(logN) |
| HashMap 为什么用 2 的幂？ | 位运算定位桶下标，效率高且分布更均匀 |
| volatile 能保证 i++ 吗？ | 不能，i++ 是读、改、写复合操作 |
| volatile 为什么能禁止重排序？ | JVM 插入内存屏障，x86 上编译成带 lock 前缀的指令 |
| DCL 单例为什么要加 volatile？ | `new` 分为分配内存、初始化、赋值三步，防止赋值被重排到初始化之前 |
| synchronized 底层靠什么实现？ | 字节码 monitorenter/monitorexit + 对象头 Mark Word + ObjectMonitor |
| synchronized 锁升级过程？ | 无锁 → 偏向锁 → 轻量级锁 → 重量级锁，只能升级不能降级 |
| 偏向锁为什么被废弃？ | 撤销需要 STW，现代应用命中率低，JDK 15 默认关闭、JDK 18 移除 |
| 轻量级锁适合什么场景？ | 线程交替执行、竞争时间极短，靠 CAS 加自旋，不适合真正同时竞争 |
| synchronized 和 Lock 怎么选？ | 简单互斥优先 synchronized，需要超时、公平、可中断时用 Lock |
| AQS 的核心是什么？ | volatile int state + CLH 双向等待队列 + 模板方法 |
| CAS 有什么问题？ | 自旋耗 CPU、只能保证单个变量、ABA、公平性差 |
| ABA 怎么解决？ | AtomicStampedReference 加版本号，或 AtomicMarkableReference 加标记 |
| AtomicLong 和 LongAdder 怎么选？ | 要精确读用 AtomicLong，高并发统计用 LongAdder |
| 乐观锁和悲观锁怎么选？ | 冲突少、读多写少用乐观锁；冲突多、长事务用悲观锁 |
| 数据库乐观锁怎么写？ | version 字段 + `where id = ? and version = ?`，判断影响行数并有限重试 |
| 反射为什么慢？ | 运行时解析和检查较多，编译器优化空间小 |
| JDK 动态代理的限制？ | 目标类需要实现接口；无接口时可考虑 CGLIB |
| Stream 中间操作何时执行？ | 遇到终止操作时才执行 |
| ThreadLocal 为什么要 remove？ | 在线程池中线程会复用，避免数据串用和内存泄漏 |
| 线程池为什么不建议 Executors？ | 默认队列或线程数可能无界，容易任务堆积或资源耗尽 |

---

## 十一、面试回答模板

回答 Java 八股时，优先采用：

    第一句：给出结论；
    第二句：说明底层原理；
    第三句：补充使用场景或优缺点；
    最后：根据追问再补代码和边界情况。

示例：回答 volatile：

> volatile 主要保证共享变量的可见性，并限制部分指令重排序，但不能保证复合操作的原子性。它适合做状态标记，不适合直接实现 i++ 这种计数操作；计数场景应使用 AtomicInteger 或锁。
