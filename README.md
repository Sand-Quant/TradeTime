# TradeTime

![](https://img.shields.io/badge/Version-1.0-red)  ![](https://img.shields.io/badge/python-3.5,3.6,3.7,3.8,3.9-blue)

![](https://img.shields.io/badge/pandas-0b3558)  ![](https://img.shields.io/badge/sandinvest-0b3558)

**TradeTime**是针对交易开发的日期时间工具，在计算上和`python`标准库`datetime`完美结合，可以灵活对日期时间进行运算操作。

- 支持和`datetime`结合使用；
- 目前**只支持A股**交易日期和交易时间，可自行导入交易日历或任意工作日历；
- 当前A股交易时间为：09:30-11:30为早盘，11:30-13:00为盘中休市，13:00-15:00为午盘；

<br>

**TradeTime** is a date and time tool developed for trading. It is computationally integrated with the `Python` standard library `datetime`, allowing flexible operation of date and time.

- Combination with `datetime`;
- Currently, only Chinese trading datetime is supported, but you are allowed to import your own trading calendar or any working calendar;

<br>

## 安装 Install

```
pip install tradetime
```

<br>

## 导入 Import

```python
# import datetime and tradetime
import datetime
import tradetime
```

<br>

## 快速使用 Quick Start！

- 获取今日交易日期

```python
>>> tradetime.date()
date(year=2022, month=5, day=19, freq='D')
```

- 获取昨日交易日期

```python
>>> tradetime.date() - 1
date(year=2022, month=5, day=18, freq='D')
```

- 获取当前周频的结束日期

```python
>>> tradetime.date().close('W') 
date(year=2022, month=5, day=20, freq='W')
```

- 获取上周周频结束日期

```python
>>> tradetime.date().close('W') - 1
date(year=2022, month=5, day=13, freq='W')
```

- 格式化

```python
>>> str(tradetime.date().close('W') + 1) 
'2022-05-27'
```



