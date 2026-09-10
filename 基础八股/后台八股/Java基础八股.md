# Java 基础面试八股

> 整理日期：2026-09-10
> 方向：后台开发 / Java 基础

---

## 一、面向对象

### Q1. 面向对象三大特性

```text
封装：隐藏内部实现，通过接口访问（private + getter/setter）
继承：子类复用父类，is-a 关系
多态：同一方法不同表现（重载 + 重写）
```

### Q2. 重载 vs 重写

| 对比 | 重载（Overload） | 重写（Override） |
|---|---|---|
| 位置 | 同类中 | 父子类中 |
| 方法名 | 相同 | 相同 |
| 参数 | 必须不同 | 必须相同 |
| 返回类型 | 可不同 | 相同或子类 |
| 修饰符 | 随意 | 不能缩小访问权限 |
| 绑定 | 编译期（静态） | 运行期（动态） |

### Q3. 接口 vs 抽象类

| 对比 | 接口 | 抽象类 |
|---|---|---|
| 继承 | 可多实现 | 只能单继承 |
| 构造方法 | 无 | 有 |
| 成员变量 | public static final | 任意 |
| 方法 | 抽象（8+ 支持 default/static） | 抽象 + 具体 |
| 场景 | 能力约定（Runnable） | 共性抽象（模板方法） |

---

## 二、String 相关

### Q4. String、StringBuilder、StringBuffer

| 类 | 可变性 | 线程安全 | 性能 |
|---|---|---|---|
| String | 不可变 | 是（天然） | 拼接慢 |
| StringBuilder | 可变 | 否 | 快 |
| StringBuffer | 可变 | 是（synchronized） | 中 |

### Q5. String 为什么不可变

```text
1. String 类 final，char[] 私有且 final（JDK 9 改为 byte[]）
2. 不可变的好处：
   - 可以做字符串常量池复用
   - 作为 HashMap key 安全（hash 不变）
   - 线程安全
   - 安全性（防止被篡改）
```

### Q6. == 和 equals 区别

```text
==：基本类型比值，引用类型比内存地址
equals：默认比地址，String/包装类重写后比值

String 高频示例：
String s1 = "abc";          // 常量池
String s2 = new String("abc");  // 堆
String s3 = s2.intern();    // 返回常量池引用

s1 == s2 → false（地址不同）
s1 == s3 → true（intern 返回常量池对象）
s1.equals(s2) → true（比值）
```

### Q7. equals 重写要重写 hashCode

```text
原因：HashMap 先按 hashCode 定位桶，再用 equals 比较
若只重写 equals：
- 两个 equals 相等的对象 hashCode 不同 → 哈希表中找不到
- 违反"equals 相等则 hashCode 必相等"契约
```

---

## 三、集合框架

### Q8. List / Set / Map 体系

```text
List：有序可重复
  - ArrayList：数组实现，查询快 O(1)，增删慢 O(n)
  - LinkedList：双向链表，增删快 O(1)，查询慢 O(n)

Set：无序不可重复
  - HashSet：HashMap 实现，O(1)
  - TreeSet：红黑树，有序 O(logN)

Map：键值对
  - HashMap：哈希表，O(1)，无序
  - TreeMap：红黑树，有序 O(logN)
```

### Q9. ArrayList vs LinkedList

| 对比 | ArrayList | LinkedList |
|---|---|---|
| 底层 | 动态数组 | 双向链表 |
| 随机访问 | O(1) | O(n) |
| 头尾增删 | O(n)（尾增 O(1) 均摊） | O(1) |
| 内存 | 连续，浪费少 | 节点分散，指针开销 |
| 适用 | 查询多 | 增删多 |

**ArrayList 扩容：** 默认容量 10，扩容为 1.5 倍。

### Q10. HashMap 原理（详见后台高频）

```text
JDK 8：数组 + 链表 + 红黑树
put 流程：hash → 定位桶 → 无冲突直接放 → 有冲突链尾插 → 树化
扩容：容量 2 倍，负载因子 0.75
线程不安全：并发 put 可能死循环（JDK 7）或数据丢失
```

### Q11. HashMap vs HashTable vs ConcurrentHashMap

| 类 | 线程安全 | 锁粒度 | 性能 |
|---|---|---|---|
| HashMap | 否 | 无 | 最快 |
| HashTable | 是 | 全表锁（方法级 synchronized） | 最差 |
| ConcurrentHashMap | 是 | JDK 7 分段锁；JDK 8 CAS + synchronized 锁桶头节点 | 好 |

### Q12. 迭代器 fail-fast

```text
原理：遍历时检测 modCount（修改次数）变化
ConcurrentModificationException：遍历中增删元素

解决：
- 用迭代器的 remove
- 用 CopyOnWriteArrayList（写时复制）
```

---

## 四、异常体系

### Q13. 异常分类

```text
Throwable
├─ Error：系统级错误（OOM、StackOverflow），不处理
└─ Exception
    ├─ RuntimeException（运行时异常）：NPE、越界、类型转换
    │   → 可以不捕获，代码逻辑问题
    └─ CheckedException（受检异常）：IOException、SQLException
        → 必须 try-catch 或 throws
```

### Q14. finally 与 return

```text
- finally 一定执行（除非 System.exit 或 JVM 崩溃）
- finally 中 return 会覆盖 try/catch 的 return
- return 表达式的值在 finally 前已确定（基本类型）
```

---

## 五、泛型

### Q15. 泛型擦除

```text
Java 泛型是编译期概念：
- 编译后类型参数被擦除，替换为限定类型（默认 Object）
- List<String> 和 List<Integer> 运行期是同一个类

影响：
- 不能 new T()、不能用基本类型作泛型参数
- 不能通过 instanceof 判断泛型具体类型
```

### Q16. 通配符

```text
?：任意类型
? extends T：上界（T 或子类），只能读不能写
? super T：下界（T 或父类），只能写不能读

口诀：PECS（Producer Extends, Consumer Super）
```

---

## 六、反射

### Q17. 反射机制

```text
概念：运行时获取类信息、创建对象、调用方法

获取 Class 对象三种方式：
1. Class.forName("com.xx.User")
2. User.class
3. user.getClass()

应用：Spring IoC、动态代理、ORM 框架、注解处理
缺点：性能较慢、破坏封装、绕过泛型检查
```

---

## 七、JDK 8 新特性

### Q18. Lambda 与函数式接口

```text
Lambda：(参数) -> { 方法体 }
本质：函数式接口的匿名实现（只有一个抽象方法的接口）

常用函数式接口：
- Function<T,R>：转换
- Predicate<T>：判断
- Consumer<T>：消费
- Supplier<T>：供给
```

### Q19. Stream 流

```text
常用操作：
filter：过滤
map：转换
sorted：排序
distinct：去重
limit：截取
collect：收集（Collectors.toList / groupingBy）

中间操作惰性执行，终止操作才触发计算
```

```java
List<String> names = users.stream()
    .filter(u -> u.getAge() > 18)
    .sorted(Comparator.comparing(User::getAge))
    .map(User::getName)
    .collect(Collectors.toList());
```

### Q20. Optional

```text
作用：优雅处理 null，避免 NPE

Optional.ofNullable(user)
    .map(User::getName)
    .orElse("未知");
```

---

## 八、IO 与序列化

### Q21. BIO / NIO / AIO

| 模型 | 原理 | 特点 |
|---|---|---|
| BIO | 阻塞 IO，一连接一线程 | 简单，资源消耗大 |
| NIO | 非阻塞 + 多路复用（Selector） | 少量线程处理多连接 |
| AIO | 异步 IO，回调通知 | 复杂，较少使用 |

**应用：** Netty 基于 NIO（主从 Reactor 模型），Tomcat 8+ 默认 NIO。

### Q22. 序列化

```text
Java 序列化：实现 Serializable，serialVersionUID 控制版本

其他方案：
- JSON（Jackson、Fastjson）：跨语言、可读
- Protobuf：高效二进制，RPC 常用
- Kryo：高性能 Java 序列化

注意：serialVersionUID 不一致会 InvalidClassException
```

---

## 九、高频追问

| 追问 | 答案要点 |
|---|---|
| String 为什么用 final | 不可变保证常量池复用和线程安全 |
| Integer 缓存范围 | -128 ~ 127，装箱复用缓存对象 |
| HashMap 为什么用红黑树 | 链表过长查询退化 O(n)，树化保证 O(logN) |
| == 比较 Integer 的坑 | 超出缓存范围装箱对象地址不同 |
| 反射为什么慢 | 动态解析、安全检查、无法内联优化 |
| Lambda 和匿名内部类区别 | Lambda 不产生新类文件，invokedynamic 实现 |
