# tradetime.bardelta

<mark>***class*** tradetime.***bardelta***(date_bars=0, time_bars=0, date_freq='D')</mark>

用于对bar进行位移计算，并获得两个`date`和`time`之间的差。

## Parameters

- **date_bars**: ***int***
  - 交易日期bar，默认为0。
- **time_bars**: ***int***
  - 交易时间bar，默认为0。
- **date_freq**: ***str***
  - 交易日期频率，默认为`D`。

<br>

## Object Instance

---

```python
>>> tradetime.bardelta()
bardelta(0)

>>> tradetime.bardelta(date_bars=1)
bardelta(date_bars=1, date_freq=D)

>>> tradetime.bardelta(date_bars=1, date_freq='W')
bardelta(date_bars=1, date_freq=W)

>>> tradetime.bardelta(time_bars=10)
bardelta(time_bars=10)
```

<br>

## Obejct Attributes

---

```python
>>> bd = tradetime.bardelta(date_bars=1, time_bars=10, date_freq='W')
>>> bd.date_bars
1
>>> bd.time_bars
10
>>> bd.date_freq
'W'
```

<br>

## Object Operators

---

- `+/-` operators

  进行运算的两个`bardelta`频率必须一致

  ```python
  >>> tradetime.bardelta(date_bars=1) + tradetime.bardelta(date_bars=2)                
  bardelta(date_bars=3, date_freq=D)
  
  >>> tradetime.bardelta(time_bars=10) - tradetime.bardelta(time_bars=5)  
  bardelta(time_bars=5)
  
  >>> tradetime.bardelta(date_bars=1) + tradetime.bardelta(date_bars=2, date_freq='W')
  
  Traceback (most recent call last):
    ...
  ValueError: D and W inconsistent
  ```


<br>

- comparison operators

  ```python
  >>> tradetime.bardelta(date_bars=1) < tradetime.bardelta(date_bars=2)
  True
  
  >>> tradetime.bardelta(date_bars=1) < tradetime.bardelta(time_bars=2) 
  False
  
  >>> tradetime.bardelta(date_bars=1) < tradetime.bardelta(date_bars=2, date_freq='W') 
  Traceback (most recent call last):
    ...
  ValueError: D and W inconsistent
  ```

<br>

- `bool` operators

  ```python
  >>> bool(tradetime.bardelta()) 
  False
  
  >>> bool(tradetime.bardelta(date_bars=1)) 
  True
  ```

  

