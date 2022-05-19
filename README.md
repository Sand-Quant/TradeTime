# TradeTime 1.0.0

快速操作交易日历

```python
>>> import tradetime
>>> tradetime.date()
date(year=2022, month=5, day=19, freq='D')

>>> tradetime.date() - 1
date(year=2022, month=5, day=18, freq='D')

>>> tradetime.date().close('W') 
date(year=2022, month=5, day=20, freq='W')

>>> tradetime.date().close('W') - 1
date(year=2022, month=5, day=13, freq='W')

>>> str(tradetime.date().close('W') + 1) 
'2022-05-27'
```

