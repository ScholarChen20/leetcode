# Python 基础面试八股

> 整理日期：2026-09-10
> 方向：后台开发 / Python

---

## 一、语言特性

### Q1. Python 是解释型还是编译型？

```text
Python 是解释型语言，但执行前会先编译为字节码（.pyc）。

执行流程：
源代码 .py → 编译 → 字节码 .pyc → PVM（Python 虚拟机）解释执行

准确说法：Python 是"解释执行"，但包含编译到字节码的步骤。
```

### Q2. 可变对象 vs 不可变对象

| 类型 | 可变性 | 对象 |
|---|---|---|
| 不可变 | 值不能改，改则新建对象 | int、float、str、tuple、frozenset |
| 可变 | 可原地修改 | list、dict、set |

```python
a = (1, 2)
a += (3,)
# 这行实际创建了新元组，a 指向新对象
```

### Q3. 深拷贝 vs 浅拷贝

```python
import copy

# 浅拷贝：只复制外层，内层对象共享引用
new_list = copy.copy(old_list)

# 深拷贝：递归复制所有层
new_list = copy.deepcopy(old_list)
```

```text
浅拷贝方式：copy.copy()、list[:]、list.copy()
深拷贝：copy.deepcopy()
判断：修改内层可变对象，浅拷贝会互相影响，深拷贝不会
```

### Q4. is 和 == 区别

```text
==：比较值相等
is：比较内存地址（是否为同一对象）

a = [1, 2, 3]
b = [1, 2, 3]
a == b → True
a is b → False
```

---

## 二、进阶语法

### Q5. 装饰器

```text
本质：接收函数返回新函数的高阶函数
作用：在不修改原函数代码的前提下扩展功能

应用：日志、鉴权、缓存、计时、路由注册（Flask）
```

```python
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"耗时: {time.time() - start:.4f}s")
        return result
    return wrapper

@timer
def do_work():
    pass
```

**带参装饰器：** 三层嵌套（外层接收装饰器参数，中层接收函数，内层是 wrapper）。

### Q6. 生成器与迭代器

| 概念 | 说明 |
|---|---|
| 可迭代对象 | 有 `__iter__` 方法（list、dict、str） |
| 迭代器 | 有 `__iter__` + `__next__` 方法，惰性取值 |
| 生成器 | 特殊迭代器，用 `yield` 定义 |

```python
# 生成器：惰性求值，省内存
def count_up(n):
    i = 0
    while i < n:
        yield i
        i += 1

gen = (x * x for x in range(10))  # 生成器表达式
```

**为什么省内存：** 不一次性产生所有元素，逐个生成。

### Q7. 闭包

```text
概念：函数内部定义函数，内层函数引用外层变量
作用：数据隐藏、保存状态
注意：修改外层变量需 nonlocal 声明
```

```python
def counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
```

---

## 三、内存与性能

### Q8. GIL（全局解释器锁）

```text
定义：CPython 解释器级别的互斥锁，同一时刻只有一个线程执行 Python 字节码

影响：
- 多线程无法利用多核 CPU 做 CPU 密集计算
- IO 密集型任务多线程仍有收益（IO 时释放 GIL）

解决方案：
1. 多进程（multiprocessing）
2. 换解释器（PyPy/Jython 无 GIL）
3. C 扩展绕过 GIL（NumPy 等）
4. Python 3.13+ 可选自由线程（实验性）
```

### Q9. 内存管理

```text
1. 引用计数：对象被引用 +1，解除引用 -1，归零回收
2. 标记-清除：解决循环引用（list 相互引用）
3. 分代回收：新对象在 0 代，存活次数越多代越老，老代回收频率低
```

```text
循环引用问题：
引用计数无法回收 a.next = b; b.next = a 的场景
→ 由标记-清除补充解决
```

### Q10. 可变默认参数陷阱

```python
# ❌ 错误写法
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2]  ← 默认列表被复用！

# ✅ 正确写法
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**原因：** 默认参数在函数定义时创建一次，之后复用同一个对象。

---

## 四、常见内置功能

### Q11. `*args` 和 `**kwargs`

```python
def func(*args, **kwargs):
    # args：位置参数打包为元组
    # kwargs：关键字参数打包为字典

func(1, 2, name="x")  # args=(1,2), kwargs={'name':'x'}

# 解包
values = [1, 2, 3]
func(*values)
config = {"name": "x"}
func(**config)
```

### Q12. 上下文管理器

```python
# with 语句自动管理资源
with open("file.txt") as f:
    content = f.read()
# 自动关闭文件，即使异常也执行 __exit__

# 自定义
class Resource:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理逻辑
        pass
```

### Q13. 常用推导式

```python
# 列表推导
squares = [x * x for x in range(10)]

# 字典推导
d = {k: v for k, v in pairs}

# 集合推导
s = {x for x in data if x > 0}

# 注意：推导式中的变量不泄漏到外层（Python 3）
```

### Q14. 鸭子类型

```text
概念："如果走起来像鸭子，叫起来像鸭子，那它就是鸭子"

不检查对象的类型，只检查它是否有需要的方法/属性
如：len() 可用于所有实现 __len__ 的对象

优点：灵活，多态不需要继承
```

---

## 五、并发编程

### Q15. 多线程 vs 多进程 vs 协程

| 方式 | 适用 | 原因 |
|---|---|---|
| 多线程 | IO 密集 | GIL 限制 CPU 密集，IO 时释放 GIL |
| 多进程 | CPU 密集 | 每个进程独立 GIL |
| 协程 | 高并发 IO | 单线程异步，切换成本极低 |

```text
threading：多线程
multiprocessing：多进程（进程间用 Queue/Pipe 通信）
asyncio：协程（await/async 语法）
```

### Q16. 协程原理

```python
import asyncio

async def fetch(url):
    # IO 等待时让出控制权
    result = await do_io(url)
    return result

async def main():
    # 并发执行多个协程
    results = await asyncio.gather(
        fetch("url1"),
        fetch("url2"),
    )
```

```text
原理：事件循环（Event Loop）
- 单线程内调度多个协程
- await IO 操作时挂起，切换其他协程
- 比线程切换开销小，支持高并发（如 1 万连接）
```

---

## 六、工程实践

### Q17. 常用虚拟环境与包管理

```text
- venv：官方自带虚拟环境
- pip：官方包管理
- poetry：依赖管理 + 打包
- uv：新一代快速包管理器
```

### Q18. 类型注解

```python
def add(a: int, b: int) -> int:
    return a + b

# 注意：注解只是提示，运行时不做强制检查
# 可用 mypy 做静态检查
```

---

## 七、高频追问

| 追问 | 答案要点 |
|---|---|
| Python 为什么慢 | 解释执行、GIL、动态类型 |
| 如何加速 Python | 多进程、C 扩展、Cython、NumPy 向量化 |
| list 和 tuple 选择 | 需要修改用 list，固定数据用 tuple（可作 dict key） |
| 字典为什么快 | 哈希表实现，O(1) 平均查找 |
| Python 传参是值传递还是引用 | 传对象引用（不可变对象效果似值传递，可变对象似引用传递） |
| 如何实现单例 | 模块导入天然单例、`__new__` 控制、装饰器 |
| del 的作用 | 减少引用计数，对象引用归零才回收 |
| range 和 xrange 区别 | Py3 中 range 就是惰性生成器（Py2 的 xrange） |
