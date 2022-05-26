# tradetime.date

<mark>***class*** tradetime.***date***(year=None, month=None, day=None, pydate=None, freq=None, ignore=False)</mark>

生成交易日期对象

## 参数 Parameters

- **year**: ***int***
  - 交易年份。
- **month**: ***int***
  - 交易月份。
- **day**: ***int***
  - 交易日。
- **pydate**: ***int, str, datetime.date, datetime.datetime***
  - int或者str，如20211231、'20211231'、'2021-12-31'；
  - python的datetime格式日期，可直接转化为tradetime.date；
- **freq**: ***str***
  - 频率，不指定则使用默认频率
- **ignore**: ***bool***
  - 是否对频率进行检查，默认True。

<br>

## 类属性 Class Attributes

---

### date.default_freqN

默认频率与频数，`V0.1.0`版本尚不支持改动`default_freqN`

```python
>>> tradetime.date.default_freqN
1
```

<br>

### date.default_freqType

```python
>>> tradetime.date.default_freqType
'D'
```

<br>

### date.[freq]

获取交易日历，支持日、周、月、季、年频：

```python
>>> tradetime.date.D           
<tradetime.Calendar object at 0x000001B429C1A8B0>

>>> tradetime.date.D.close.head()
0    2005-01-04
1    2005-01-05
2    2005-01-06
3    2005-01-07
4    2005-01-10
Name: date, dtype: object
```

<br>

获取季度交易日历，通过`open`和`close`获取该频率的起始bar，为`pd.Series`格式：

```python
>>> tradetime.date.Q.open.head()
0    2005-01-04
1    2005-04-01
2    2005-07-01
3    2005-10-10
4    2006-01-04
Name: date, dtype: object

>>> tradetime.date.Q.close.head()   
0    2005-03-31
1    2005-06-30
2    2005-09-30
3    2005-12-30
4    2006-03-31
Name: date, dtype: object
```

<br>

### date.calendar_open/date.calendar_close/date.calendar

获取交易日历**字典**，同样用于提取交易日历

```python
>>> tradetime.date.calendar.keys()
dict_keys(['D', 'W', 'M', 'Q', 'Y'])

>>> tradetime.date.calendar['D'].head()
0    2005-01-04
1    2005-01-05
2    2005-01-06
3    2005-01-07
4    2005-01-10
Name: time, dtype: object

>>> tradetime.date.calendar_open['Y'].head()
0    2005-01-04
1    2006-01-04
2    2007-01-04
3    2008-01-02
4    2009-01-05
Name: time, dtype: object
```

<br>

## 类方法 Class Methods

### date.bars

<mark>tradetime.date.***bars***(start_date, end_date, freq=None, is_open=False, overflow=False)</mark>

获取一段时间区间的交易日期

**Parameters:**

- **start_date**: ***_AnyDatetime_Type***
  - 开始日期

- **end_date**: ***_AnyDatetime_Type***
  - 结束日期
- **freq**: ***str***
  - 指定频率
- **is_open**: ***bool***
  - bars是否为开始日期，默认False。
- **overflow**: ***bool***
  - 结束日期是否溢出，默认False。

**Returns:**

- ***pd.Series***

  交易日期所处对应频率交易日历的位置

**Examples:**

```python
# 一段时间的open bars
>>> tradetime.date.bars(datetime.date(2022, 2, 1), datetime.date(2022, 3, 12), freq='W', is_open=True)
0    2022-02-07
1    2022-02-14
2    2022-02-21
3    2022-02-28
4    2022-03-07

# 一段时间的close bars
>>> tradetime.date.bars(datetime.date(2022, 2, 1), datetime.date(2022, 3, 12), freq='W')
0    2022-02-11
1    2022-02-18
2    2022-02-25
3    2022-03-04
4    2022-03-11
Name: date, dtype: object

# 允许溢出
>>> tradetime.date.bars(datetime.date(2022, 2, 1), datetime.date(2022, 3, 12), freq='W', overflow=True) 
0    2022-02-11
1    2022-02-18
2    2022-02-25
3    2022-03-04
4    2022-03-11
5    2022-03-18
```

<br>

### date.quarter_range

<mark>tradetime.date.***quarter_range***(start_date, end_date, type_: type = None, fmt: str = None, **kw_bars)</mark>

获取一段季度日期，可以自定义格式

**Parameters:**

- **start_date**: ***_AnyDatetime_Type***
  - 开始日期

- **end_date**: ***_AnyDatetime_Type***
  - 结束日期
- **type_**: ***type***
  - 指定类型，可以为str
- **fmt**: ***str***
  - 自定义格式，默认'2022Q1'
- **kw_bars**:
  - 可以传入`date.bars`其他参数

**Returns:**

- ***pd.Series***

  一段季度日期

**Examples:**

```python
# 每个季度的最后一个交易日
>>> tradetime.date.quarter_range(20200101, 20201231)
0    2020-03-31
1    2020-06-30
2    2020-09-30
3    2020-12-31
Name: date, dtype: object

# 每个季度的首个交易日
>>> tradetime.date.quarter_range(20200101, 20201231, is_open=True) 
0    2020-01-02
1    2020-04-01
2    2020-07-01
3    2020-10-09
        
>>> tradetime.date.quarter_range(20200101, 20201231, type_=str)
0    2020Q1
1    2020Q2
2    2020Q3
3    2020Q4
Name: date, dtype: object

>>> tradetime.date.quarter_range(20200101, 20201231, type_=str, fmt='Year(y)Quarter(q)') 
0    Year2020Quarter1
1    Year2020Quarter2
2    Year2020Quarter3
3    Year2020Quarter4
Name: date, dtype: object
```

<br>

### date.current

<mark>tradetime.date.***current***(freq=None, if_break: str = None)</mark>

获取当前所处的bar

**Parameters:**

- **freq**: ***str***
  - 指定频率
- **if_break**: **str**
  - 非交易日处理，可选`'past'`、`'future'`、`None`；
  - `'past'`表示取历史日期，`'future'`表示取未来日期，`None`表示正常处理；

**Returns:**

- ***tradetime.date***

  当前所处的bar

**Examples:**

```python
# 假设今天为 2022-03-20
>>> tradetime.date.current()
date(year=2022, month=3, day=21, freq='D')

>>> tradetime.date.current('W') 
date(year=2022, month=3, day=25, freq='W')

>>> tradetime.date.current('Q') 
date(year=2022, month=3, day=31, freq='Q')

# 假设今天为 2022-01-01非交易日
>>> tradetime.date.current() 
Traceback (most recent call last):   
	...     
ValueError: The date is external break, missing param if_break.
    
>>> tradetime.date.current(if_break='past')                                                
date(year=2019, month=12, day=31, freq='D')
```

<br>

### date.future

<mark>tradetime.date.***future***(n=1, freq=None)</mark>

获取未来第n个bar，默认下一个，**不支持非交易日使用**

**Parameters:**

- **n**: ***int***
  - 位移数量，默认为1
- **freq**: ***str***
  - 指定频率，默认为默认频率

**Returns:**

- ***tradetime.date***

  未来的bar

**Examples:**

```python
# 假设今天为 2022-03-20
>>> tradetime.date.future(n=1, freq='W') 
date(year=2022, month=4, day=1, freq='W')

>>> tradetime.date.future(n=1, freq='Q')  
date(year=2022, month=6, day=30, freq='Q')
```

```python
# 假设今天为 2022-04-01
>>> tradetime.date.future()     
date(year=2022, month=4, day=6, freq='D')
>>> tradetime.date.previous()
date(year=2022, month=3, day=31, freq='D')
```

<br>

### date.previous

<mark>tradetime.date.***previous***(n=1, freq=None)</mark>

获取之前第n个bar，默认上一个，**不支持非交易日使用**

**Parameters:**

- **n**: ***int***
  - 位移数量，默认为1
- **freq**: ***str***
  - 指定频率

**Returns:**

- ***tradetime.date***

  之前的bar

**Examples:**

```python
# 假设今天为 2022-03-20
>>> tradetime.date.previous(n=1, freq='Q') 
date(year=2021, month=12, day=31, freq='Q')

>>> tradetime.date.previous(n=1, freq='W')  
date(year=2022, month=3, day=18, freq='W')
```

<br>

### date.is_trading

<mark>tradetime.date.***is_trading***(d=None)</mark>

判断该日期是否为**交易日**

**Parameters:**

- **d**: ***_AnyDatetime_Type***
  - 日期

**Returns:**

- ***bool***

  是否为交易日

**Examples:**

```python
>>> tradetime.date.is_trading(datetime.date(2022, 3, 18)) 
True

>>> tradetime.date.is_trading(datetime.date(2022, 3, 19)) 
False
```

<br>

### date.is_break

<mark>tradetime.date.***is_break***(d=None)</mark>

判断该日期是否为**非交易日**

**Parameters:**

- **d**: ***_AnyDatetime_Type***
  - 日期

**Returns:**

- ***bool***

  是否为非交易日

**Examples:**

```python
>>> tradetime.date.is_break(datetime.date(2022, 3, 18))   
False

>>> tradetime.date.is_break(datetime.date(2022, 3, 19))   
True
```

<br>

### date.break_type

<mark>tradetime.date.***break_type***(d=None, freq='D')</mark>

判断非交易日类型，分为时间段间非交易日和时间段内非交易日

**Parameters:**

- **d**: ***_AnyDatetime_Type***
  - 日期
- **freq**: ***str***
  - 频率

**Returns:**

- ***str***

  非交易日类型

**Examples:**

```python
>>> tradetime.date.break_type(20200101, 'D') 
'external break'
>>> tradetime.date.break_type(20200101, 'W') 
'internal break'
>>> tradetime.date.break_type(20200101, 'M') 
'external break'
>>> tradetime.date.break_type(20200101, 'Q') 
'external break'
>>> tradetime.date.break_type(20200101, 'Y') 
'external break'
```

<br>

### date.get_close

<mark>tradetime.date.***get_close***(year=None, q=None, m=None)</mark>

获取某年某个季度或者某个月份的最后一个交易日期

**Parameters:**

- **year**: ***int***
  - 年份
- **q**: ***int***
  - 第几个季度，只能为`1,2,3,4`
- **m**: ***int***
  - 第几个月，只能为`1-12`

**Returns:**

- ***tradetime.date***

  最后一个交易日

**Examples:**

```python
>> > tradetime.date.get_close(2021, m=7)
date(year=2021, month=7, day=30, freq='M')

>> > tradetime.date.get_close(2021, q=3)
date(year=2021, month=9, day=30, freq='Q')
```

<br>

### date.get_open

<mark>tradetime.date.***get_open***(year=None, q=None, m=None)</mark>

获取某年某个季度或者某个月份的第一个交易日期

**Parameters:**

- **year**: ***int***
  - 年份
- **q**: ***int***
  - 第几个季度，只能为`1,2,3,4`
- **m**: ***int***
  - 第几个月，只能为`1-12`

**Returns:**

- ***tradetime.date***

  第一个交易日

```python
>> > tradetime.date.get_open(2021, m=7)
date(year=2021, month=7, day=1, freq='M')

>> > tradetime.date.get_open(2021, q=3)
date(year=2021, month=7, day=1, freq='Q')
```

<br>

### date.set_option

<mark>tradetime.date.***set_option***(default_freq: str = 'D')</mark>

设置tradetime.date的默认频率

**Parameters:**

- **default_freq**: ***str***
  - 频率

**Returns:**

- None

**Examples:**

```python
# 将默认频率设置为周频
>>> tradetime.date.set_option('W')  
```

<br>

## 类实例 Object Instance

---

- 没有参数时，默认按照今天创建交易日期

  ```python
  # 今日是2022-04-28
  
  >>> tradetime.date()
  date(year=2022, month=4, day=28, freq='D')
  
  >>> tradetime.date(freq='W') 
  Traceback (most recent call last):
  	...
  ValueError: 2022-04-28 doesn't match freq W
  ```

- 查看当前默认频率，创建实例`tradetime.date`,并自动进行检查是否满足该频率bar的close

  ```python
  >>> tradetime.date.default_freqType
  'D'
  >>> tradetime.date(2022, 3, 18)
  date(year=2022, month=3, day=18, freq='D')
  ```

<br>

- 或者将`datetime.date`转换为`tradetime.date`实例：

  ```python
  >>> tradetime.date(pydate=datetime.date(2022, 3, 18)) 
  date(year=2022, month=3, day=18, freq='D')
  ```

<br>

- 对于不满足默认频率的交易日期，将抛出`ValueError`，但也可以通过`ignore`参数关闭该检查：

  ```python
  >>> tradetime.date(pydate=datetime.date(2022, 3, 19)) 
  Traceback (most recent call last):
    ...
  ValueError: 2022-03-19 doesn't match freq D
  
  >>> tradetime.date(pydate=datetime.date(2022, 3, 19), ignore=True) 
  date(year=2022, month=3, day=19, freq='D')
  ```
  
- 可通过**指定频率**，创建非日频交易日期，同样可以通过`ignore`参数关闭检查：

  ```python
  >>> tradetime.date(2021, 12, 24, freq='W') 
  date(year=2021, month=12, day=24, freq='W')
  
  >>> tradetime.date(2021, 12, 25, freq='W')              
  Traceback (most recent call last):                                                   
  	...                  
  ValueError: 2021-12-25 doesn't match freq W
  
  >>> tradetime.date(2021, 12, 25, freq='W', ignore=True) 
  date(year=2021, month=12, day=25, freq='W')
  ```

<br>

## 类实例属性 Object Attributes

---

将`date`默认频率设置为`M`月频，接下来查看其属性：

```python
>>> tradetime.set_date('M') 

>>> d = tradetime.date(2022, 3, 31) 

>>> d
date(year=2022, month=3, day=31, freq='M')
```

### date.year

```python
>>> d.year
2022
```

### date.quarter

```python
>>> d.quarter
1   
```

### date.month

```python
>>> d.month
3
```

### date.day

```python
>>> d.day
31
```

### date.ignore

```python
>>> d.ignore
False
```

### date.freq

```python
>>> d.freq
'M'
```

<br>

## 类实例方法 Object Methods

---

### date.index

<mark>tradetime.date.***index***(freq: str = None)</mark>

获取交易日期所处指定频率交易日历的索引位置

**Parameters:**

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`

**Returns:**

- ***int***

  交易日期所处对应频率交易日历的位置

**Examples:**

```python
>>> tradetime.date(2022, 3, 31, freq='M').index()
206
>>> tradetime.date(2022, 3, 31, freq='M').index('D') 
4189
```

<br>

### date.validate

<mark>tradetime.date.***validate***(freq: str = None)</mark>

验证对象是否符合该频率

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`

**Returns:**

- ***bool***

  是否符合频率

**Examples:**

```python
>>> tradetime.date(2022, 3, 31, freq='M').validate() 
True
>>> tradetime.date(2022, 3, 31, freq='M').validate('W') 
False
```

<br>

### date.open

<mark>tradetime.date.***open***(freq: str = None, if_break: str = None)</mark>

获取频率对应bar开始日期，接受交易日和非交易日

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`
- **if_break**: **str**
  - 非交易日处理，可选`'past'`、`'future'`、`None`；
  - `'past'`表示取历史日期，`'future'`表示取未来日期，`None`表示正常处理；

**Returns:**

- ***tradetime.date***

  日期所处频率对应bar的开始日期

**Examples:**

```python
# 默认为M，2022-03-31处在2022年3月bar，第一个交易日为2022-03-01
>> > tradetime.date(2022, 3, 31, freq='M').open()
date(year=2022, month=3, day=1, freq='M')

# 设置为周频，则对应周bar第一个交易日为2022-03-28
>> > tradetime.date(2022, 3, 31, freq='M').open('W')
date(year=2022, month=3, day=28, freq='W')
```

如果当天是**时间段内非交易日**：

```python
>>> d = tradetime.date(pydate=20200101, freq='D', ignore=True) 
>>> d
date(year=2020, month=1, day=1, freq='D')

# 判断是否为交易日
>>> tradetime.date.is_break(d) 
True

# 指定频率，判断非交易日类型
>>> tradetime.date.break_type(d, 'W') 
'internal break'

# 时间段内非交易日
>>> d.open('W') 
date(year=2019, month=12, day=30, freq='W')
>>> d.open('W', 'future') 
date(year=2020, month=1, day=6, freq='W')
>>> d.open('W', 'past')   
date(year=2019, month=12, day=23, freq='W')
```

如果当天是**时间段间非交易日**：

```python
>>> tradetime.date.break_type(d, 'M')
'external break'

# 时间段间非交易日
>>> d.open('M') 
Traceback (most recent call last):
	...
ValueError: The date is external break, missing param if_break.
    
>>> d.open('M', 'past') 
date(year=2019, month=12, day=2, freq='M')
>>> d.open('M', 'future') 
date(year=2020, month=1, day=2, freq='M')
```

<br>

### date.close

<mark>tradetime.date.***close***(freq: str = None, if_break: str = None)</mark>

获取频率对应bar结束日期，接受交易日和非交易日

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`
- **if_break**: **str**
  - 非交易日处理，可选`'past'`、`'future'`、`None`；
  - `'past'`表示取历史日期，`'future'`表示取未来日期，`None`表示正常处理；

**Returns:**

- ***tradetime.date***

  日期所处频率对应bar的结束日期

**Examples:**

```python
>> > tradetime.date(2022, 3, 31, freq='M').close()
date(year=2022, month=3, day=31, freq='M')

>> > tradetime.date(2022, 3, 31, freq='M').close('W')
date(year=2022, month=4, day=1, freq='W')
```

如果当天是**时间段内非交易日**：

```python
>>> d = tradetime.date(pydate=20200101, freq='D', ignore=True) 
>>> d
date(year=2020, month=1, day=1, freq='D')

# 判断是否为交易日
>>> tradetime.date.is_break(d) 
True

# 指定频率，判断非交易日类型
>>> tradetime.date.break_type(d, 'W') 
'internal break'

# 时间段内非交易日
>>> d.close('W') 
date(year=2020, month=1, day=3, freq='W')
>>> d.close('W', 'past') 
date(year=2019, month=12, day=27, freq='W')
>>> d.close('W', 'future') 
date(year=2020, month=1, day=10, freq='W')
```

如果当天是**时间段间非交易日**：

```python
>>> tradetime.date.break_type(d, 'M')
'external break'

# 时间段间非交易日
>>> d.close('M') 
Traceback (most recent call last):
	...
ValueError: The date is external break, missing param if_break.
    
>>> d.close('M', 'past')  
date(year=2019, month=12, day=31, freq='M')
>>> d.close('M', 'future') 
date(year=2020, month=1, day=23, freq='M')
```

<br>

### date.range

<mark>tradetime.date.***range***(freq: str = None, if_break: str = None)</mark>

获取频率对应bar的开始和结束日期区间

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`
- **if_break**: **str**
  - 非交易日处理，可选`'past'`、`'future'`、`None`；
  - `'past'`表示取历史日期，`'future'`表示取未来日期，`None`表示正常处理；

**Returns:**

- ***Tuple[datetime.date, datetime.date]***

  日期所处频率对应bar的开始和结束日期区间

**Examples:**

```python
>>> tradetime.date(2022, 3, 31, freq='M').range('W') 
(date(year=2022, month=3, day=28, freq='W'), date(year=2022, month=4, day=1, freq='W'))

>>> tradetime.date(2022, 3, 31, freq='M').range('Y') 
(date(year=2022, month=1, day=4, freq='Y'), date(year=2022, month=12, day=30, freq='Y'))


# 如果是非交易日
>>> tradetime.date(2020, 1, 1, freq='M', ignore=True).range('M', 'past') 
(date(year=2019, month=12, day=2, freq='M'), date(year=2019, month=12, day=31, freq='M'))

>>> tradetime.date(2020, 1, 1, freq='M', ignore=True).range('M', 'future') 
(date(year=2020, month=1, day=2, freq='M'), date(year=2020, month=1, day=23, freq='M'))
```

<br>

### date.is_open

<mark>tradetime.date.***is_open***(freq: str = None)</mark>

判断是否为该频率的开始日期

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`

**Returns:**

- ***bool***

  是否为该频率的开始日期

**Examples:**

```python
# 一开始指定为'M'频率，需要ignore，然后判断是否为该频率的open
>> > tradetime.date(2022, 3, 1, freq='M', ignore=True).is_open()
True
# 检查一个日频交易日期，是否为月频上的open
>> > tradetime.date(2022, 3, 1, freq='D').is_open('M')
True
```

<br>

### date.is_close

<mark>tradetime.date.***is_close***(freq: str = None)</mark>

判断是否为该频率的结束日期

**Parameters**:

- **freq**: ***str***
  - 频率，默认为`tradetime.date.freq`

**Returns:**

- ***bool***

  是否为该频率的结束日期

**Examples:**

```python
>> > tradetime.date(2022, 3, 1, freq='D').is_close('M')
False
>> > tradetime.date(2022, 3, 31, freq='D').is_close('M')
True
>> > tradetime.date(2022, 3, 31, freq='M').is_close()
True
```

<br>

### date.py_date

<mark>tradetime.date.***py_date***()</mark>

```python
>>> tradetime.date(2022, 1, 4).py_date() 
datetime.date(2022, 1, 4)
```

<br>

### date.pd_date

<mark>tradetime.date.***pd_date***()</mark>

```python
>>> tradetime.date(2022, 1, 4).pd_date() 
DatetimeIndex(['2022-01-04'], dtype='datetime64[ns]', freq=None)
```

<br>

### date.nearest

<mark>tradetime.date.***nearest***(if_break: str = None)</mark>

获取最近的一个交易日，当本身就是交易日时，返回自己

**Parameters**:

- **if_break**: **str**
  - 非交易日处理，可选`'past'`和`'future'`；
  - `'past'`：向历史取最近的一个交易日；
  - `'future'`：向未来取最近的一个交易日；

**Returns:**

- ***bool***

  是否为该频率的结束日期

**Examples:**

```python
>>> d = tradetime.date(pydate=20200101, freq='D', ignore=True) 
>>> d
date(year=2020, month=1, day=1, freq='D')

>>> d.close('M', 'past')
Traceback (most recent call last):                                                
	...
ValueError: The date is break, missing param if_break.     
 
>>> d.nearest('past')
date(year=2019, month=12, day=31, freq='D')

>>> d.nearest('future')
date(year=2020, month=1, day=2, freq='D')
```

<br>

## 实例运算符 Object Operators

### Bar位移

- 和`int`，进行bar位移

  ```python
  # 加法
  >>> tradetime.date(2022, 3, 18, freq='D') + 3 
  date(year=2022, month=3, day=23, freq='D')
  
  >>> tradetime.date(2022, 3, 18, freq='W') + 3 
  date(year=2022, month=4, day=8, freq='W')
  
  # 减法
  >>> tradetime.date(2022, 3, 18, freq='D') - 3  
  date(year=2022, month=3, day=15, freq='D')
  
  >>> tradetime.date(2022, 3, 18, freq='W') - 3 
  date(year=2022, month=2, day=25, freq='W')
  
  # 不建议反向进行加减，这样做会很奇怪
  >>> tradetime.date.operation_inverse = True  # 必须设置后才可以反向运算
  
  >>> 3 + tradetime.date(2022, 3, 18, freq='D')
  date(year=2022, month=3, day=23, freq='D')
  >>> 3 - tradetime.date(2022, 3, 18, freq='D')
  date(year=2022, month=3, day=15, freq='D')
  ```

<br>

- 和`tradetime.bardelta`，进行bar位移

  ```python
  >>> tradetime.date(2022, 3, 18, freq='D') + tradetime.bardelta(date_bars=2)                
  date(year=2022, month=3, day=22, freq='D')
  
  # 必须频率一致
  >>> tradetime.date(2022, 3, 18, freq='D') + tradetime.bardelta(date_bars=2, date_freq='Q') 
  Traceback (most recent call last):                                                        
    ...
  ValueError: 2022-03-18 is not in freq 'Q'
   
  >>> tradetime.date(2022, 3, 18, freq='D') - tradetime.bardelta(date_bars=2)                
  date(year=2022, month=3, day=16, freq='D')
  
  # 同样不建议反向进行加减，这样做会很奇怪
  ```

<br>

### 时间位移

- 和`datetime.delta`，进行时间位移，**而不是bar位移**，不考虑是否为交易日；

  ```python
  >>> tradetime.date(2022, 3, 18, freq='D') + datetime.timedelta(days=2) 
  date(year=2022, month=3, day=20, freq='D')
  
  >>> tradetime.date(2022, 3, 18, freq='W') + datetime.timedelta(days=3) 
  date(year=2022, month=3, day=21, freq='W')
  
  # 同样不建议反向进行加减，这样做会很奇怪
  ```

<br>

### 求差

- 和`tradetime.date`，求差，频率必须相同

  ```python
  >>> tradetime.date(2022, 3, 31, freq='M') - tradetime.date(2022, 1, 28, freq='M')
  bardelta(date_bars=2, date_freq=M)
  
  # 默认日频，表示相差三个交易日
  >>> tradetime.date(2022, 3, 31) - tradetime.date(2022, 3, 28) 
  bardelta(date_bars=3, date_freq=D)
  ```

<br>

## 实例比较符 Object Comparison

- 与`tradetime.date`，与频率无关

  ```python
  >>> tradetime.date(2022, 3, 1, freq='D') < tradetime.date(2022, 3, 31, freq='Q') 
  True
  ```

<br>

- 与`datetime`，与频率无关

  ```python
  >>> tradetime.date(2022, 3, 1, freq='D') == datetime.date(2022, 3, 1)            
  True
  
  # 默认今天，2022-03-20
  >>> tradetime.date(2022, 3, 1, freq='D') < datetime.time()            
  True
  ```

  

