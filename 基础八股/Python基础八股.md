# Python 基础八股

## 一、Python 基础概念

### 1. Python 是什么类型的语言？

**参考答案：**

Python 是一种高级、解释型、动态类型语言，同时支持面向对象、面向过程和函数式编程。

主要特点包括：

- 语法简单，开发效率高；
- 动态类型，不需要提前声明变量类型；
- 一切皆对象；
- 拥有丰富的标准库和第三方库；
- 支持面向对象、函数式和异步编程；
- 由解释器负责执行代码。

Python 常用于 Web 开发、数据分析、人工智能、自动化、爬虫和脚本开发等场景。

---

### 2. Python 是编译型语言还是解释型语言？

**参考答案：**

通常把 Python 称为解释型语言，但这个说法并不完全准确。

以 CPython 为例，Python 代码执行过程大致是：

```text
Python 源代码
    ↓
编译成字节码
    ↓
Python 虚拟机执行字节码
```

因此，Python 不是简单地逐行翻译执行，而是先将源代码编译成字节码，再由 Python 虚拟机执行。

---

### 3. Python 解释器的作用是什么？

**参考答案：**

Python 解释器负责读取、分析和执行 Python 代码，同时还负责：

- 创建和管理 Python 对象；
- 管理内存；
- 执行函数和模块；
- 处理异常；
- 进行垃圾回收；
- 调用底层系统功能。

最常见的 Python 解释器是 CPython，它主要使用 C 语言实现。

执行：

```bash
python demo.py
```

其中的 `python` 命令本质上就是启动 Python 解释器。

---

### 4. Python 中变量是如何存储的？

**参考答案：**

Python 中变量本质上保存的是对象的引用，而不是对象本身。

```python
a = 10
```

可以理解为：

```text
变量 a ─────→ 整数对象 10
```

多个变量可以指向同一个对象：

```python
a = [1, 2]
b = a

b.append(3)

print(a)  # [1, 2, 3]
```

因为 `a` 和 `b` 引用了同一个列表对象。

---

## 二、数据类型和运算

### 5. Python 常见的数据类型有哪些？

**参考答案：**

常见数据类型包括：

- 数字类型：`int`、`float`、`complex`
- 布尔类型：`bool`
- 字符串：`str`
- 列表：`list`
- 元组：`tuple`
- 字典：`dict`
- 集合：`set`
- 空值类型：`NoneType`
- 字节类型：`bytes`

其中：

- `list`、`dict`、`set` 通常是可变对象；
- `int`、`float`、`str`、`tuple` 通常是不可变对象。

---

### 6. `is` 和 `==` 有什么区别？

**参考答案：**

`==` 比较两个对象的值是否相等。

`is` 比较两个变量是否指向同一个对象，也就是比较对象的身份地址。

```python
a = [1, 2]
b = [1, 2]
c = a

print(a == b)  # True
print(a is b)  # False

print(a == c)  # True
print(a is c)  # True
```

一般来说：

- 判断值是否相等，使用 `==`；
- 判断是否为 `None`，推荐使用 `is None`。

```python
if value is None:
    pass
```

---

### 7. 什么是可变对象和不可变对象？

**参考答案：**

可变对象创建后，内容可以被修改，但对象本身的身份不变。

常见可变对象：

```python
list
dict
set
```

常见不可变对象：

```python
int
float
str
tuple
bool
```

示例：

```python
items = [1, 2]
old_id = id(items)

items.append(3)

print(id(items) == old_id)  # True
```

列表内容发生了变化，但列表对象本身没有改变。

字符串不能直接修改：

```python
s = "abc"
s = s + "d"
```

这实际上创建了一个新的字符串对象。

---

### 8. `list`、`tuple`、`set` 和 `dict` 有什么区别？

**参考答案：**

| 类型 | 特点 | 是否有序 | 是否允许重复 | 是否可变 |
|---|---|---|---|---|
| `list` | 有序集合 | 是 | 是 | 是 |
| `tuple` | 不可变序列 | 是 | 是 | 否 |
| `set` | 无重复集合 | 不保证顺序 | 否 | 是 |
| `dict` | 键值对集合 | 保持插入顺序 | key 不允许重复 | 是 |

使用场景：

- `list`：保存有序且可能重复的数据；
- `tuple`：保存不希望被修改的数据；
- `set`：去重、集合运算；
- `dict`：根据 key 快速查找 value。

---

### 9. `list` 和 `tuple` 有什么区别？

**参考答案：**

主要区别如下：

1. `list` 可变，`tuple` 不可变；
2. `list` 通常占用更多内存；
3. `tuple` 由于不可变，访问效率通常略高；
4. `tuple` 可以作为字典的 key，`list` 不可以；
5. 需要修改数据时使用 `list`，不需要修改时可以使用 `tuple`。

```python
items = [1, 2, 3]
items.append(4)

values = (1, 2, 3)
```

---

### 10. `dict` 为什么查询速度比较快？

**参考答案：**

Python 的字典底层基于哈希表实现。

查找数据时，Python 会：

1. 对 key 计算哈希值；
2. 根据哈希值定位数组位置；
3. 在对应位置查找 key；
4. 返回对应的 value。

平均情况下，字典的查询、插入和删除时间复杂度都是：

```text
O(1)
```

但如果出现大量哈希冲突，性能可能下降。

字典的 key 必须是可哈希对象，例如字符串、数字、元组等不可变对象通常可以作为 key，列表不能作为 key。

---

### 11. `append` 和 `extend` 有什么区别？

**参考答案：**

`append` 将一个对象作为整体添加到列表末尾。

```python
items = [1, 2]
items.append([3, 4])

print(items)  # [1, 2, [3, 4]]
```

`extend` 会遍历传入对象，并将其中的元素逐个添加到列表中。

```python
items = [1, 2]
items.extend([3, 4])

print(items)  # [1, 2, 3, 4]
```

---

### 12. `sort` 和 `sorted` 有什么区别？

**参考答案：**

`sort` 是列表对象的方法，会直接修改原列表，并且返回 `None`。

```python
items = [3, 1, 2]
items.sort()

print(items)  # [1, 2, 3]
```

`sorted` 是内置函数，不会修改原对象，而是返回一个新的列表。

```python
items = [3, 1, 2]
result = sorted(items)

print(items)   # [3, 1, 2]
print(result)  # [1, 2, 3]
```

---

## 三、函数和参数

### 13. `*args` 和 `**kwargs` 是什么？

**参考答案：**

`*args` 用来接收任意数量的位置参数，函数内部会将它们组织成一个元组。

`**kwargs` 用来接收任意数量的关键字参数，函数内部会将它们组织成一个字典。

```python
def demo(*args, **kwargs):
    print(args)
    print(kwargs)

demo(1, 2, name="Tom", age=18)
```

结果可以理解为：

```python
(1, 2)
{"name": "Tom", "age": 18}
```

它们常用于参数数量不固定的函数，也常用于装饰器。

---

### 14. `*args` 和 `**kwargs` 中的 `*` 和 `**` 还有什么作用？

**参考答案：**

除了收集参数，`*` 和 `**` 还可以进行参数解包。

列表解包：

```python
numbers = [1, 2, 3]

print(*numbers)
```

等价于：

```python
print(1, 2, 3)
```

字典解包：

```python
params = {
    "name": "Tom",
    "age": 18
}

demo(**params)
```

等价于：

```python
demo(name="Tom", age=18)
```

---

### 15. Python 函数参数的传递方式是什么？

**参考答案：**

Python 采用“对象引用传递”，也可以理解为“传递对象引用的副本”。

如果传入的是不可变对象，函数内部修改变量不会影响外部变量：

```python
def change(value):
    value += 1

number = 10
change(number)

print(number)  # 10
```

如果传入的是可变对象，函数内部可以修改对象内容：

```python
def change(items):
    items.append(3)

values = [1, 2]
change(values)

print(values)  # [1, 2, 3]
```

---

### 16. 为什么不建议使用可变对象作为默认参数？

**参考答案：**

函数默认参数只会在函数定义时创建一次，而不是每次调用时重新创建。

错误示例：

```python
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2]
```

多次调用使用的是同一个列表。

推荐写法：

```python
def add_item(item, items=None):
    if items is None:
        items = []

    items.append(item)
    return items
```

---

### 17. 什么是 LEGB 规则？

**参考答案：**

Python 查找变量时通常遵循 LEGB 规则：

- `L`：Local，局部作用域；
- `E`：Enclosing，外层函数作用域；
- `G`：Global，全局作用域；
- `B`：Built-in，内置作用域。

```python
name = "global"

def outer():
    name = "enclosing"

    def inner():
        name = "local"
        print(name)

    inner()

outer()
```

查找顺序是：

```text
局部作用域 → 外层函数作用域 → 全局作用域 → 内置作用域
```

---

### 18. `global` 和 `nonlocal` 有什么区别？

**参考答案：**

`global` 用于声明使用全局变量。

```python
count = 0

def add():
    global count
    count += 1
```

`nonlocal` 用于在嵌套函数中修改外层函数的局部变量。

```python
def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1

    inner()
    return count
```

---

## 四、装饰器、迭代器和生成器

### 19. 什么是装饰器？

**参考答案：**

装饰器是一种在不修改原函数代码的情况下，为函数增加额外功能的机制。

常见用途包括：

- 日志记录；
- 权限校验；
- 函数计时；
- 缓存；
- 事务处理；
- 参数校验。

```python
from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用函数：{func.__name__}")
        result = func(*args, **kwargs)
        return result

    return wrapper

@log
def hello(name):
    print(f"Hello, {name}")
```

下面两种写法等价：

```python
@log
def hello():
    pass
```

```python
def hello():
    pass

hello = log(hello)
```

---

### 20. 为什么装饰器中通常使用 `*args` 和 `**kwargs`？

**参考答案：**

因为装饰器可能包装参数数量和类型不同的函数。

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

这样无论原函数接收位置参数还是关键字参数，都可以正常传递。

通常还建议使用 `functools.wraps`，以保留原函数的名称、文档字符串等元信息。

---

### 21. 什么是可迭代对象、迭代器和生成器？

**参考答案：**

可迭代对象是可以被 `for` 循环遍历的对象，例如列表、元组、字符串和字典。

迭代器是实现了 `__iter__()` 和 `__next__()` 方法的对象，每次调用 `next()` 返回一个元素。

生成器是一种特殊的迭代器，通常通过 `yield` 创建。

```python
def numbers():
    yield 1
    yield 2
    yield 3

generator = numbers()

print(next(generator))  # 1
print(next(generator))  # 2
```

生成器具有惰性计算的特点，不会一次性生成所有数据，适合处理大量数据。

---

### 22. `yield` 和 `return` 有什么区别？

**参考答案：**

`return` 会结束函数并返回结果。

`yield` 会暂停函数执行，保存当前状态，下次调用时从暂停位置继续执行。

```python
def demo():
    yield 1
    yield 2

for value in demo():
    print(value)
```

生成器的优势是节省内存，适合处理大文件、大数据流和分页数据。

---

## 五、异常和文件处理

### 23. Python 中如何处理异常？

**参考答案：**

使用 `try-except` 捕获异常：

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("除数不能为 0")
```

完整结构包括：

```python
try:
    pass
except Exception:
    pass
else:
    pass
finally:
    pass
```

含义：

- `try`：执行可能出错的代码；
- `except`：捕获异常；
- `else`：没有异常时执行；
- `finally`：无论是否异常都会执行。

---

### 24. `raise` 的作用是什么？

**参考答案：**

`raise` 用于主动抛出异常。

```python
def check_age(age):
    if age < 0:
        raise ValueError("年龄不能小于 0")
```

也可以重新抛出当前异常：

```python
try:
    do_something()
except Exception:
    log_error()
    raise
```

---

### 25. 如何定义自定义异常？

**参考答案：**

自定义异常通常继承自 `Exception`。

```python
class InvalidAgeError(Exception):
    pass

def check_age(age):
    if age < 0:
        raise InvalidAgeError("年龄不能小于 0")
```

自定义异常可以让代码中的错误类型更加明确。

---

### 26. Python 中如何安全地读取文件？

**参考答案：**

推荐使用 `with`，它可以自动关闭文件。

```python
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
```

`with` 执行结束后，即使发生异常，文件也会被自动关闭。

常见文件模式：

- `r`：只读；
- `w`：覆盖写；
- `a`：追加写；
- `b`：二进制模式；
- `+`：读写模式。

---

### 27. `with` 的底层原理是什么？

**参考答案：**

`with` 依赖上下文管理器。上下文管理器需要实现：

```python
__enter__()
__exit__()
```

进入 `with` 时调用 `__enter__()`，离开时调用 `__exit__()`。

```python
class Manager:
    def __enter__(self):
        print("进入上下文")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("退出上下文")

with Manager():
    print("执行代码")
```

常见应用包括文件操作、数据库连接、锁和事务管理。

---

## 六、面向对象

### 28. 什么是类和对象？

**参考答案：**

类是对象的模板，用来描述对象的属性和行为。

对象是类的具体实例。

```python
class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print(f"Hello, {self.name}")

person = Person("Tom")
person.say_hello()
```

其中：

- `Person` 是类；
- `person` 是对象；
- `name` 是属性；
- `say_hello` 是方法。

---

### 29. `self` 是什么？

**参考答案：**

`self` 表示当前对象本身。

```python
class Person:
    def __init__(self, name):
        self.name = name
```

调用：

```python
person = Person("Tom")
```

可以理解为：

```python
Person.__init__(person, "Tom")
```

`self` 不是 Python 关键字，只是一种约定俗成的命名方式。

---

### 30. `__init__` 和 `__new__` 有什么区别？

**参考答案：**

`__new__` 负责创建对象，`__init__` 负责初始化对象。

一般执行顺序是：

```text
__new__() → __init__()
```

通常情况下只需要重写 `__init__`：

```python
class Person:
    def __init__(self, name):
        self.name = name
```

如果需要控制对象的创建过程，例如实现单例模式，才可能重写 `__new__`。

---

### 31. Python 支持哪些面向对象特性？

**参考答案：**

Python 支持：

- 封装；
- 继承；
- 多态；
- 抽象；
- 方法重写；
- 鸭子类型。

示例：

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        print("汪汪")

class Cat(Animal):
    def speak(self):
        print("喵喵")
```

`Dog` 和 `Cat` 都重写了 `speak` 方法，调用时会表现出不同的行为，这就是多态。

---

### 32. `staticmethod` 和 `classmethod` 有什么区别？

**参考答案：**

静态方法使用 `@staticmethod` 修饰，不会自动传入实例或类。

```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b
```

类方法使用 `@classmethod` 修饰，第一个参数通常是 `cls`，表示当前类。

```python
class Person:
    count = 0

    @classmethod
    def get_count(cls):
        return cls.count
```

区别：

- 实例方法：第一个参数是 `self`；
- 类方法：第一个参数是 `cls`；
- 静态方法：没有自动传入的 `self` 或 `cls`。

---

### 33. `@property` 有什么作用？

**参考答案：**

`@property` 可以把方法转换成类似属性的访问方式，同时在访问和修改时加入逻辑控制。

```python
class Person:
    def __init__(self, age):
        self._age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("年龄不能小于 0")
        self._age = value
```

使用时：

```python
person = Person(18)
print(person.age)

person.age = 20
```

---

## 七、浅拷贝和深拷贝

### 34. 什么是浅拷贝和深拷贝？

**参考答案：**

浅拷贝只复制最外层对象，内部嵌套对象仍然共享引用。

深拷贝会递归复制所有嵌套对象，复制结果与原对象完全独立。

```python
import copy

source = [[1, 2], [3, 4]]

shallow = copy.copy(source)
deep = copy.deepcopy(source)
```

修改嵌套列表：

```python
source[0].append(5)
```

此时：

- `shallow` 可能受到影响；
- `deep` 不会受到影响。

---

## 八、内存管理和垃圾回收

### 35. Python 是如何管理内存的？

**参考答案：**

Python 的内存管理主要由解释器负责，包括：

- 对象创建；
- 引用计数；
- 垃圾回收；
- 内存池管理；
- 内存分配和释放。

Python 程序员通常不需要手动释放普通对象，但仍然需要及时关闭文件、数据库连接和网络连接等外部资源。

---

### 36. 什么是引用计数？

**参考答案：**

引用计数是 CPython 主要使用的一种内存管理方式。

当一个对象被引用时，引用计数增加；当引用消失时，引用计数减少。当引用计数变为 0 时，对象通常会被立即释放。

```python
a = []
b = a
```

此时列表对象至少有两个引用。

```python
del a
del b
```

当所有引用都消失后，该对象就具备被释放的条件。

---

### 37. 什么是循环引用？

**参考答案：**

循环引用是指多个对象相互引用，形成环状结构。

```python
a = []
b = []

a.append(b)
b.append(a)
```

即使外部变量不再使用这两个列表，它们仍然互相引用，引用计数不会降为 0。

Python 的垃圾回收器会检测不可达的循环引用，并对其进行回收。

---

### 38. Python 对象变得不可达后，一定会被回收吗？

**参考答案：**

不一定。

对象不可达只能说明它具备被垃圾回收的条件，并不代表一定会立即回收。

垃圾回收的时机由 Python 解释器和垃圾回收机制决定。对于 CPython，普通对象在引用计数归零时通常会较快释放，但循环引用可能要等待垃圾回收器处理。

此外，程序如果很快退出，也可能没有经历完整的垃圾回收过程。

因此，不能依赖垃圾回收来释放文件句柄、数据库连接和网络连接等外部资源，这些资源应该显式关闭。

---

### 39. Python 中的 `del` 是删除对象吗？

**参考答案：**

`del` 删除的是变量或引用关系，不一定直接删除对象。

```python
items = [1, 2, 3]
other = items

del items
```

执行 `del items` 后，只是删除了变量 `items`，但对象仍然被 `other` 引用，因此不会被释放。

只有当对象不再被任何变量引用，并且没有其他引用关系时，才可能被回收。

---

## 九、线程、进程和协程

### 40. 什么是 GIL？

**参考答案：**

GIL 是 Global Interpreter Lock，即全局解释器锁，主要存在于传统 CPython 实现中。

它保证同一时刻只有一个线程执行 Python 字节码，因此多线程不能充分利用多个 CPU 核心执行 Python 代码。

但线程在执行 I/O 操作时通常会释放 GIL，所以多线程仍然适合 I/O 密集型任务，例如：

- 网络请求；
- 文件读写；
- 数据库访问。

对于 CPU 密集型任务，通常使用多进程更合适。

---

### 41. 多线程、多进程和协程有什么区别？

**参考答案：**

| 类型 | 特点 | 适用场景 |
|---|---|---|
| 多线程 | 同一进程内共享内存 | I/O 密集型任务 |
| 多进程 | 进程之间内存隔离 | CPU 密集型任务 |
| 协程 | 用户态任务切换 | 高并发 I/O 任务 |

简单理解：

- 多线程：多个线程交替执行；
- 多进程：多个进程真正并行；
- 协程：一个线程中多个任务主动切换。

---

### 42. Python 的异步机制是什么？

**参考答案：**

Python 异步机制主要通过 `asyncio` 实现，核心思想是：

> 当一个任务等待 I/O 时，主动让出执行权，让事件循环执行其他任务。

核心组成：

- `async def`：定义协程；
- `await`：等待异步操作；
- 事件循环：负责调度协程和 I/O 事件；
- `asyncio.gather`：并发运行多个任务。

示例：

```python
import asyncio

async def task(name, delay):
    print(f"{name} 开始")
    await asyncio.sleep(delay)
    print(f"{name} 完成")

async def main():
    await asyncio.gather(
        task("任务1", 2),
        task("任务2", 1),
    )

asyncio.run(main())
```

两个任务可以交替执行，总耗时接近最长任务的耗时。

---

### 43. 异步适合什么场景？

**参考答案：**

异步适合 I/O 密集型任务，例如：

- 网络请求；
- Web 服务；
- 数据库访问；
- 爬虫；
- 高并发连接；
- 文件读写。

异步不适合直接解决 CPU 密集型计算。如果异步任务中执行了长时间的同步计算或阻塞函数，也会阻塞整个事件循环。

---

## 十、模块和工程化

### 44. `if __name__ == "__main__"` 有什么作用？

**参考答案：**

每个 Python 文件都有一个 `__name__` 变量。

当文件被直接运行时：

```python
__name__ == "__main__"
```

当文件被其他模块导入时：

```python
__name__ == "模块名"
```

因此可以使用：

```python
def main():
    print("程序开始执行")

if __name__ == "__main__":
    main()
```

这样可以保证只有直接运行该文件时才执行 `main()`，被导入时不会自动执行。

---

### 45. 模块和包有什么区别？

**参考答案：**

模块通常就是一个 `.py` 文件。

包通常是一个包含多个模块的目录，传统上需要包含 `__init__.py` 文件。

示例：

```text
project/
├── main.py
└── utils/
    ├── __init__.py
    ├── string_utils.py
    └── file_utils.py
```

其中：

- `string_utils.py` 是模块；
- `utils` 是包。

---

### 46. 什么是虚拟环境？

**参考答案：**

虚拟环境可以为不同项目创建相互隔离的 Python 运行环境和依赖包。

创建虚拟环境：

```bash
python -m venv venv
```

激活虚拟环境：

Windows：

```bash
venv\Scripts\activate
```

Linux 或 macOS：

```bash
source venv/bin/activate
```

虚拟环境可以避免不同项目之间的依赖版本冲突。

---

## 十一、常见时间复杂度

### 47. 常见 Python 容器操作的时间复杂度是什么？

**参考答案：**

常见情况如下：

| 操作 | 平均时间复杂度 |
|---|---:|
| 列表按下标访问 | O(1) |
| 列表末尾追加 | O(1) |
| 列表中间插入 | O(n) |
| 列表删除中间元素 | O(n) |
| 列表查找元素 | O(n) |
| 字典查询 | O(1) |
| 字典插入 | O(1) |
| 字典删除 | O(1) |
| 集合查询 | O(1) |
| 集合插入 | O(1) |
| 列表排序 | O(n log n) |

字典和集合的复杂度是平均情况，极端哈希冲突时性能可能下降。

---

### 48. 为什么列表头部插入和删除比较慢？

**参考答案：**

Python 列表底层类似动态数组，元素在内存中通常是连续存储的。

如果在列表头部插入元素，后面的元素需要整体向后移动：

```python
items.insert(0, value)
```

时间复杂度通常是：

```text
O(n)
```

如果需要频繁从两端插入或删除，可以使用 `collections.deque`：

```python
from collections import deque

queue = deque()
queue.append(1)
queue.appendleft(2)
```

---

## 十二、综合面试题

### 49. Python 中如何选择合适的数据结构？

**参考答案：**

可以根据数据特点选择：

- 需要有序、允许重复：使用 `list`；
- 数据不希望被修改：使用 `tuple`；
- 需要快速判断是否存在或去重：使用 `set`；
- 需要通过 key 查找 value：使用 `dict`；
- 需要频繁从两端插入删除：使用 `deque`；
- 需要优先级处理：使用 `heapq`。

选择数据结构时需要综合考虑：

- 是否有序；
- 是否允许重复；
- 是否需要修改；
- 查询和插入的频率；
- 时间复杂度；
- 内存占用。

---


## 十三、高频追问

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