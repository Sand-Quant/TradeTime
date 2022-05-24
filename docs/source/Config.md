# Config

## tradetime.set_date

<mark>tradetime.***set_date***(default_freq: str = 'D')</mark>

设置交易日期，将默认交易日期设置为日、周、月、季、年频率。

**Parameters:**

- **default_freq**: ***str***
  - 交易日期频率，可选择参数为`D,W,M,Q,Y`，默认为`D`。所有设置的日期将默认通过该频率进行检验，判断是否符合交易日期频率；

**Returns:**

- **None**

<br>

**Examples**

---

- 设置为`D`日线频率

  ```python
  >>> tradetime.set_date()  # default 'D'
  ```

  在日线频率上，`2022-03-18`是交易日，而`2022-03-20`不是交易日，因此在创建`2022-03-20`时会抛出`ValueError`：

  ```python
  >>> tradetime.date(2022, 3, 18)
  date(year=2022, month=3, day=18, freq='D')
  
  >>> tradetime.date(2022, 3, 20)
  Traceback (most recent call last):
   ...
  ValueError: 2022-03-20 doesn't match freq D
  ```

  可以通过`tradetime.date`的`ignore`参数关闭该检查：

  ```python
  >>> tradetime.date(2022, 3, 20, ignore=True)
  date(year=2022, month=3, day=20, freq='D')
  ```

  <br>

- 设置为`Q`季度频率

  ```python
  >>> tradetime.set_date('Q')
  ```

  `2022-03-31`是2022Q1季度，而`2022-03-18`虽然是交易日，但并不符合季度频率，因此抛出`ValueError`：

  ```python
  >>> tradetime.date(2022, 3, 31)
  date(year=2022, month=3, day=31, freq='Q')
  
  >>> tradetime.date(2022, 3, 18)
  Traceback (most recent call last):
    ...
  ValueError: 2022-03-18 doesn't match freq Q
  ```

  <br>

## tradetime.set_time

<mark>tradetime.***set_time***(bars=241, freq='1min')</mark>

设置交易时间，设置为241bar的1分钟频率、240bar的1分钟频率，以及其它频率。

**Parameters**:

- **bars**: ***int***

  - 一分钟频率bar的数量，只接受240和241，默认241。

    （1）<mark>241</mark>表示一分钟频率第一根bar为`09:30`；

    （2）<mark>240</mark>表示一分钟频率第一根bar为`09:31`，将`09:30`纳入`09:31`。

- **freq**: ***str***

  - 时间频率，可选择参数为`<x>min,<x>T,<x>H`，默认为`1min`。`min,T`代表分钟频率，`H`代表小时频率，`<x>`代表几分钟或者几小时，换算为分钟数必须被120整除。
  - 当频率不为`1min`时，`bars`参数不再起作用。

**Returns**:

- **None**

<br>

**Examples**

---

- 设置为`241 bar`的`1min`频率

  ```python
  >>> tradetime.set_time()  # default setting
  ```

  `09:30`和`09:31`均符合，而`09:28`不符合该频率的bar会抛出`ValueError`，同样可以通过`tradetime.time`的`ignore`参数忽略自动检查：

  ```python
  >>> tradetime.time(9, 30)
  time(hour=9, minute=30, second=0, freq='1min')
  
  >>> tradetime.time(9, 31)
  time(hour=9, minute=31, second=0, freq='1min')
  
  >>> tradetime.time(9, 28)
  Traceback (most recent call last):
  	...
  ValueError: time(hour=9, minute=28, second=0, freq='1min') is not match freq
  
  >>> tradetime.time(9, 28, ignore=True)
  time(hour=9, minute=28, second=0, freq='1min')
  ```

  <br>

- 设置为`240 bar`的`1min`频率

  ```python
  >>> tradetime.set_time(bars=240)
  ```

  此时`09:30`不符合，而`09:31`均符合

  ```python
  >>> tradetime.time(9, 30)
  Traceback (most recent call last):
    ...
  ValueError: time(hour=9, minute=30, second=0, freq='1min') is not match freq
  
  >>> tradetime.time(9, 31)
  time(hour=9, minute=31, second=0, freq='1min')
  ```

  <br>

- 设置为`15min`频率

  ```python
  >>> tradetime.set_time(freq='15min')
  ```

  此时`10:25`不符合，而`10:30`均符合

  ```python
  >>> tradetime.time(10, 25)
  Traceback (most recent call last):
    ...
  ValueError: time(hour=10, minute=25, second=0, freq='15min') is not match freq
  
  >>> tradetime.time(10, 30)
  time(hour=10, minute=30, second=0, freq='15min')
  ```

