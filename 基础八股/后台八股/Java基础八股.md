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

### Q36. Java 并发的三大特性是什么？

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

### Q39. volatile 有什么作用？

volatile 主要保证可见性，并限制部分指令重排序。

适合状态标记：

    private volatile boolean running = true;

不能保证复合操作的原子性：

    count++;

计数场景应使用 AtomicInteger 或锁。

### Q40. 什么是 CAS？有什么问题？

CAS 是比较并交换：比较内存值是否等于预期值，相等则更新，否则失败重试。

优点：非阻塞，适合简单原子更新。

问题：

- 失败重试会消耗 CPU；
- 不适合直接保护多个变量的一致性；
- 可能出现 ABA；
- 高竞争下性能可能下降。

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
| synchronized 和 Lock 怎么选？ | 简单互斥优先 synchronized，需要超时、公平、可中断时用 Lock |
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
