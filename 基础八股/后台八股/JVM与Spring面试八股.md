# JVM 与 Spring 全家桶面试八股

> 整理日期：2026-09-08
> 方向：后台开发 / JVM / Spring

---

# 第一部分：JVM

## J1. JVM 内存模型（运行时数据区）

```text
线程私有：
- 程序计数器：当前执行指令地址，唯一不 OOM 的区域
- 虚拟机栈：方法调用栈帧（局部变量、操作数栈），StackOverflowError
- 本地方法栈：Native 方法

线程共享：
- 堆：对象实例，GC 主要区域，OOM 高发区
- 方法区（元空间）：类信息、常量、静态变量（JDK 8 后移入本地内存）
```

**高频追问：**

```text
Q: 堆和栈的区别？
A: 堆存对象（共享、GC 管理），栈存方法调用（私有、自动释放）

Q: 什么情况 StackOverflow？什么情况 OOM？
A: 无限递归 → StackOverflow；对象过多且无法回收 → Heap OOM
```

---

## J2. 对象创建过程

```text
1. 类加载检查：类是否已加载
2. 分配内存：指针碰撞 / 空闲列表（取决于 GC）
3. 内存初始化为零值
4. 设置对象头（哈希、GC 分代年龄、锁状态）
5. 执行构造函数
```

---

## J3. 垃圾回收

### 判断对象存活

```text
1. 引用计数法：循环引用问题（Python 用，Java 不用）
2. 可达性分析：GC Roots 出发，不可达对象可回收（Java 使用）

GC Roots 包含：
- 栈中局部变量引用的对象
- 静态变量引用的对象
- 常量引用
- 本地方法栈引用
```

### 垃圾回收算法

| 算法 | 优点 | 缺点 |
|---|---|---|
| 标记-清除 | 简单 | 内存碎片 |
| 复制 | 无碎片、效率高 | 内存利用率 50% |
| 标记-整理 | 无碎片 | 移动成本高 |

### 分代收集

```text
新生代（Eden : S0 : S1 = 8:1:1）：
- 新对象进 Eden
- Minor GC：Eden 存活 → S0/S1 复制，年龄 +1
- 年龄达到 15（默认）晋升老年代

老年代：
- 大对象直接进入
- Major GC / Full GC
```

### 垃圾收集器

| 收集器 | 特点 | 适用 |
|---|---|---|
| Serial | 单线程，STW | 单核小应用 |
| Parallel | 多线程，吞吐优先 | 后台计算 |
| CMS | 并发标记，低延迟 | 响应优先（已废弃） |
| G1 | 分区收集，可预测停顿 | 大堆（主流） |
| ZGC | 超低延迟（<10ms） | 大内存低延迟 |

**G1 特点：** 把堆划分为多个 Region，按回收价值优先级回收垃圾最多的 Region。

---

## J4. 类加载机制

### 类加载过程

```text
加载 → 验证 → 准备 → 解析 → 初始化 → 使用 → 卸载
```

### 双亲委派模型

```text
Bootstrap ClassLoader（JDK 核心类）
    ↑ 先委派给父类加载
Extension ClassLoader（扩展类）
    ↑
Application ClassLoader（应用类）

加载流程：自底向上询问是否已加载，自顶向下尝试加载
```

**为什么用双亲委派：**

```text
1. 避免类重复加载
2. 防止核心类被篡改（如自定义 java.lang.String 不会生效）
```

**打破双亲委派：** Tomcat 的 WebAppClassLoader（隔离多个 Web 应用的类）、SPI 机制。

---

## J5. 调优与排查

### 常用 JVM 参数

```text
-Xms：初始堆大小
-Xmx：最大堆大小
-Xss：线程栈大小
-XX:NewRatio：老年代/新生代比例
-XX:MaxMetaspaceSize：元空间上限
-XX:+PrintGCDetails：打印 GC 日志
-XX:+HeapDumpOnOutOfMemoryError：OOM 时生成堆转储
```

### OOM 排查思路

```text
1. 加 -XX:+HeapDumpOnOutOfMemoryError 参数
2. 用 MAT / JProfiler 分析 heap dump
3. 找出占用内存最大的对象和引用链
4. 判断是内存泄漏还是堆配置过小
5. 泄漏 → 修复代码；过小 → 调参
```

### 线上 CPU 飙高排查

```text
1. top 找到高 CPU 的 Java 进程 PID
2. top -Hp PID 找到高 CPU 的线程 TID
3. printf '%x' TID 转十六进制
4. jstack PID | grep 十六进制 TID 定位代码行
```

### 内存泄漏常见原因

```text
- 静态集合持有对象不放
- 未关闭的资源（连接、流）
- 监听器未注销
- ThreadLocal 未 remove
```

---

# 第二部分：Spring

## S1. IoC 与 AOP

### IoC（控制反转）

```text
概念：对象创建和管理交给容器，而非业务代码 new

容器：BeanFactory（基础）、ApplicationContext（常用）

好处：
- 解耦：依赖由容器注入
- 统一管理生命周期
- 便于测试和替换实现
```

### 依赖注入方式

```text
1. 构造器注入：推荐，依赖不可变
2. Setter 注入：可选依赖
3. 字段注入（@Autowired）：简单但不利于测试
```

### AOP（面向切面编程）

```text
概念：把横切逻辑（日志、事务、权限）从业务中抽离

术语：
- Aspect：切面（类）
- Pointcut：切入点（哪些方法）
- Advice：通知（何时执行）
  Before / After / Around / AfterReturning / AfterThrowing
- JoinPoint：连接点（方法调用）

应用场景：事务管理、日志记录、权限校验、性能监控
```

---

## S2. Bean 生命周期

```text
1. 实例化：反射创建对象
2. 属性填充：依赖注入
3. Aware 回调：BeanNameAware、BeanFactoryAware
4. BeanPostProcessor 前置处理
5. 初始化：@PostConstruct → InitializingBean → init-method
6. BeanPostProcessor 后置处理（AOP 代理在此生成）
7. 使用
8. 销毁：@PreDestroy → DisposableBean → destroy-method
```

**面试重点：** AOP 代理是在 BeanPostProcessor 后置处理阶段生成的。

---

## S3. 循环依赖

### 什么是循环依赖

```text
A 依赖 B，B 依赖 A
构造器注入循环依赖：无法解决，抛异常
Setter/字段注入循环依赖：Spring 通过三级缓存解决
```

### 三级缓存

| 缓存 | 存放内容 |
|---|---|
| 一级缓存 singletonObjects | 完整 Bean |
| 二级缓存 earlySingletonObjects | 提前暴露的 Bean（未完成注入） |
| 三级缓存 singletonFactories | Bean 工厂（生成代理对象） |

**解决流程：**

```text
创建 A → 放入三级缓存 → 注入 B
→ 创建 B → 注入 A（从三级缓存拿 A 的早期引用）
→ B 完成 → A 完成
```

**为什么用三级缓存：** 二级缓存存普通对象，三级缓存存工厂，是为了提前生成 AOP 代理对象，保证注入的是代理而不是原始对象。

---

## S4. Spring 事务失效场景

```text
1. 方法非 public：@Transactional 无效
2. 同类内部调用：this.method() 不走代理，事务失效
3. 异常被捕获：try-catch 吞掉异常不回滚
4. 异常类型不对：默认只回滚 RuntimeException，受检异常不回滚
5. 数据库引擎不支持事务（MyISAM）
6. 多线程调用：事务不跨线程
7. 传播行为设置错误
```

**同类调用解决方案：**

```text
1. 拆到不同类
2. 注入自身代理（@Autowired 自己）
3. AopContext.currentProxy()（需开启 exposeProxy）
```

---

## S5. SpringBoot 自动装配

### 原理

```text
@SpringBootApplication
  = @SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan

@EnableAutoConfiguration
  → @Import(AutoConfigurationImportSelector)
  → 读取 META-INF/spring.factories
  → 加载 xxxAutoConfiguration 类
  → @ConditionalOnClass / @ConditionalOnMissingBean 条件装配
```

**自定义 Starter 步骤：**

```text
1. 写配置属性类（@ConfigurationProperties）
2. 写自动配置类（@Configuration + @ConditionalOnXxx）
3. 在 spring.factories 注册自动配置类
4. 打包发布
```

---

## S6. SpringMVC 请求流程

```text
1. 请求进入 DispatcherServlet
2. HandlerMapping 找到对应 Handler（@RequestMapping）
3. HandlerAdapter 调用 Controller 方法
4. 返回 ModelAndView / 数据
5. 视图解析 / 消息转换（HttpMessageConverter）
6. 响应返回
```

**拦截器 vs 过滤器：**

| 对比 | Filter | Interceptor |
|---|---|---|
| 归属 | Servlet 规范 | Spring 框架 |
| 作用范围 | 所有请求 | 走 DispatcherServlet 的请求 |
| 时机 | 进入 Servlet 前 | Handler 前后 |
| 用途 | 编码、跨域 | 鉴权、日志 |

---

## S7. 高频追问

| 追问 | 答案要点 |
|---|---|
| Spring 用了哪些设计模式 | 工厂、单例、代理、模板方法、观察者等 |
| @Autowired 和 @Resource 区别 | @Autowired 按类型，@Resource 默认按名称 |
| BeanFactory 和 ApplicationContext | 前者懒加载基础容器，后者扩展（事件、国际化） |
| SpringBoot 和 Spring 区别 | 自动装配、内嵌容器、约定优于配置 |
| 事务传播 REQUIRES_NEW 场景 | 子事务独立提交，日志记录等 |
| AOP 失效场景 | 同类调用、非 public、动态代理限制 |
---

## 归档：计网-操作系统中的 JVM 与 Spring 内容

3) JVM介绍

<img src="https://cdn.paicoding.com/tobebetterjavaer/images/sidebar/sanfene/jvm-3.png" alt="三分恶面渣逆袭：Java虚拟机运行时数据区" style="zoom:50%;" />

虚拟机栈：当线程执行一个方法时，会创建一个对应的[栈帧](https://javabetter.cn/jvm/stack-frame.html)，用于存储局部变量表、操作数栈、动态链接、方法出口等信息，然后栈帧会被压入虚拟机栈中。当方法执行完毕后，栈帧会从虚拟机栈中移除。



<img src="https://cdn.paicoding.com/stutymore/jvm-20240404091445.png" alt="二哥的 Java 进阶之路：对象的创建过程" style="zoom:33%;" />

4) G1收集器
G1 收集器的运行过程大致可划分为这几个步骤：

①、**并发标记**，G1 通过并发标记的方式找出堆中的垃圾对象。并发标记阶段与应用线程同时执行，不会导致应用线程暂停。

②、**混合收集**，在并发标记完成后，G1 会计算出哪些区域的回收价值最高（也就是包含最多垃圾的区域），然后优先回收这些区域。这种回收方式包括了部分新生代区域和老年代区域。  选择回收成本低而收益高的区域进行回收，可以提高回收效率和减少停顿时间。

③、**可预测的停顿**，G1 在垃圾回收期间仍然需要「Stop the World」。不过，G1 在停顿时间上添加了预测机制，用户可以 JVM 启动时指定期望停顿时间，G1 会尽可能地在这个时间内完成垃圾回收。

类从被加载到 JVM 开始，到卸载出内存，整个生命周期分为七个阶段，分别是载入、验证、准备、解析、初始化、使用和卸载。其中验证、准备和解析这三个阶段统称为连接。

5) 双亲委派机制

双亲委派模型要求类加载器在加载类时，先委托父加载器尝试加载，只有父加载器无法加载时，子加载器才会加载。
**①、避免类的重复加载**：父加载器加载的类，子加载器无需重复加载。
**②、保证核心类库的安全性**：如 `java.lang.*` 只能由 Bootstrap ClassLoader 加载，防止被篡改

### Spring

# Spring
**使用 IoC 思想的开发方式** ：不通过 new 关键字来创建对象，而是通过 IoC 容器(Spring 框架) 来帮助我们实例化对象。我们需要哪个对象，直接从 IoC 容器里面去取即可

<img src="https://oss.javaguide.cn/github/javaguide/system-design/framework/spring/aspectj-advice-types.jpg" alt="img" style="zoom:50%;" />

日志记录：自定义日志记录注解，利用 AOP，一行代码即可实现日志记录。
性能统计：利用 AOP 在目标方法的执行前后统计方法的执行时间，方便优化和分析。
事务管理：`@Transactional` 注解可以让 Spring 为我们进行事务管理比如回滚异常操作，免去了重复的事务管理逻辑。`@Transactional`注解就是基于 AOP 实现的。
