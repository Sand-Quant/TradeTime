import re
import os
import sys
import bisect
import importlib
import time as _time
import datetime as _datetime
import calendar as _calendar
from typing import List, Tuple, Dict, Optional, TypeVar

import pandas as pd

# Package Attributes
__project__ = 'SandValue'.lower()
__package__ = 'TradeTime'.lower()
try:
    # Use Self Path
    __packagePath__ = importlib.import_module(__package__).__spec__.submodule_search_locations[0]
except TypeError:
    # If enter by __main__ == __name__
    __packagePath__ = os.path.dirname(importlib.import_module(__package__).__spec__.origin)
except ModuleNotFoundError:
    # Otherwise, Use Project Path
    __packagePath__ = importlib.import_module('.'.join([__project__, __package__])).__spec__.submodule_search_locations[0]

# python datetime type
_datetime_type = (_datetime.datetime, _datetime.date, _datetime.time)
_anydatetime_type = (str, int, _datetime.datetime, _datetime.date, _datetime.time)
_Datetime_Type = TypeVar('_Datetime_Type', _datetime.datetime, _datetime.date, _datetime.time)
_AnyDatetime_Type = TypeVar('_AnyDatetime_Type', str, int, _datetime.datetime, _datetime.date, _datetime.time)

# python datetime
py_date = _datetime.date
py_time = _datetime.time
py_datetime = _datetime.datetime
py_timedelta = _datetime.timedelta

# frequency type
_freq_date_type = ['D', 'W', 'M', 'Q', 'Y']
_freq_hour_type = ['H']
_freq_minute_type = ['min', 'T']
_freq_second_type = ['s']
_freq_time_type = _freq_minute_type + _freq_hour_type + _freq_second_type


def _check_time_bars(bars: int):
    assert bars == 240 or bars == 241, "1min bars should be 240 or 241"


def _check_time_freq(freq: str):
    n = int(re.sub(u"([^\u0030-\u0039])", "", freq))
    type_ = re.sub(u"([^\u0041-\u007a])", "", freq)
    assert type_ in _freq_time_type, f"{type_} is not in {_freq_time_type}"
    if type_ in _freq_minute_type:
        assert 120 % n == 0, "freq minute should be divisible by 120, like 1,2,3,4,5,6,10,...,120"
    if type_ in _freq_hour_type:
        assert n in [1, 2], "freq hour should be 1 or 2"
    if type_ in _freq_second_type:
        assert 60 % n == 0, "freq second should be divisible by 120, like 1,2,3,4,5,6,10,...,60"


def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def _datetime2time(x):
    """transfer python datetime object to tradetime.time object"""
    if isinstance(x, _datetime.datetime):
        x = x.time()
    if isinstance(x, _datetime.date):
        x = _datetime.time()
    if isinstance(x, _datetime.time):
        x = time(hour=x.hour, minute=x.minute, second=x.second, ignore=True)
    assert isinstance(x, time)
    return x


def _convert2date(x=None, freq=None) -> 'date':
    """transfer str or datetime object to tradetime.date object
    None
    int: YYYYMMDD
    str: YYYYMMDD or YYYY-MM-DD
    datetime.date
    datetime.time
    datetime.datetime
    """
    if x is None:
        x = _datetime.date.today()
    if isinstance(x, int):
        x = str(x)
    if isinstance(x, str):
        if '-' not in x:
            try:
                x = f"{x[:4]}-{x[4:6]}-{x[6:]}"
            except Exception:
                raise TypeError(f"Invalid format: '{x}'")
        x = _datetime.date.fromisoformat(x[:10])
    if isinstance(x, _datetime.datetime):
        x = x.date()
    if isinstance(x, _datetime.time):  # 只给时间默认日期为今天
        x = _datetime.date.today()
    if isinstance(x, _datetime.date):
        x = date(year=x.year, month=x.month, day=x.day, freq=freq, ignore=True)
    else:
        raise TypeError(f"Invalid format: '{x}'")
    return x


def _convert2time(x=None, freq=None) -> 'time':
    """transfer str or datetime object to tradetime.time object
    None
    int: HHMMSS
    str: HHMMSS or HH:MM:SS
    datetime.date
    datetime.time
    datetime.datetime
    """
    if x is None:
        x = _datetime.datetime.now().time()
    if isinstance(x, int):
        x = str(x)
    if isinstance(x, str):
        if ':' not in x:
            try:
                x = f"{x[:2]}:{x[2:4]}:{x[4:]}"
            except Exception:
                raise TypeError(f"Invalid format: '{x}'")
        x = _datetime.time.fromisoformat(x[:8])
    if isinstance(x, _datetime.datetime):
        x = x.time()
    if isinstance(x, _datetime.date):  # 只给时间默认日期为今天
        x = _datetime.datetime.now().time()
    if isinstance(x, _datetime.time):
        x = time(hour=x.hour, minute=x.minute, second=x.second, freq=freq, ignore=True)
    else:
        raise TypeError(f"Invalid format: '{x}'")
    return x


class _Time(_datetime.time):
    """自定义datetime.time类，增加加减功能"""

    def __add__(self, other: _datetime.timedelta):
        assert isinstance(other, _datetime.timedelta)
        return (_datetime.datetime.combine(_datetime.date.today(), self) + other).time()

    def __sub__(self, other: _datetime.timedelta):
        assert isinstance(other, _datetime.timedelta)
        return (_datetime.datetime.combine(_datetime.date.today(), self) - other).time()


class Calendar:

    def __init__(self, freq):
        self._freq = freq
        # Load Data From Anywhere, but pd.Series type.
        calendar: pd.Series = pd.read_csv(os.path.join(__packagePath__, 'data.csv'))['time']
        calendar = pd.to_datetime(calendar)
        calendar.index = pd.to_datetime(calendar)

        _open = calendar.resample(self._freq).first().dropna().reset_index(drop=True)
        _close = calendar.resample(self._freq).last().dropna().reset_index(drop=True)
        self._open = _open.apply(lambda x: date(x.year, x.month, x.day, freq=freq, ignore=True))
        self._close = _close.apply(lambda x: date(x.year, x.month, x.day, freq=freq, ignore=True))

    @property
    def open(self) -> pd.Series:
        return self._open

    @property
    def close(self) -> pd.Series:
        return self._close

    @property
    def range(self) -> Tuple[pd.Series, pd.Series]:
        return self._open, self._close


class Session:

    # 早盘开始和结束时间
    morning_open_time = _Time(hour=9, minute=30)
    morning_close_time = _Time(hour=11, minute=30)
    # 午盘开始和结束时间
    afternoon_open_time = _Time(hour=13, minute=0)
    afternoon_close_time = _Time(hour=15, minute=0)
    # 是否包含开盘集合竞价
    include = True

    def __init__(self, freq):
        self._freq = freq
        _check_time_freq(self._freq)

        if freq == '1min':
            if self.include:
                morning_session = self.time_range(
                    start=self.morning_open_time,
                    end=self.morning_close_time,
                    freq=freq
                )
            else:  # bars == 240
                morning_session = self.time_range(
                    start=self.morning_open_time + _datetime.timedelta(minutes=1),
                    end=self.morning_close_time,
                    freq=freq
                )
            afternoon_session = self.time_range(
                start=self.afternoon_open_time + _datetime.timedelta(minutes=1),
                end=self.afternoon_close_time,
                freq=freq
            )
        elif freq == '1s':
            if self.include:
                morning_session = self.time_range(
                    start=self.morning_open_time,
                    end=self.morning_close_time,
                    freq=freq
                )
            else:
                self.morning_open_time + _datetime.timedelta(seconds=1)
                morning_session = self.time_range(
                    start=self.morning_open_time + _datetime.timedelta(seconds=1),
                    end=self.morning_close_time,
                    freq=freq
                )
            afternoon_session = self.time_range(
                start=self.afternoon_open_time + _datetime.timedelta(seconds=1),
                end=self.afternoon_close_time,
                freq=freq
            )
        else:  # other freq type
            morning_session = self.time_range(
                start=self.morning_open_time,
                end=self.morning_close_time,
                freq=freq
            )
            afternoon_session = self.time_range(
                start=self.afternoon_open_time,
                end=self.afternoon_close_time,
                freq=freq
            )

        # 计算Open Bar
        freq_n = int(re.sub(u"([^\u0030-\u0039])", "", freq))
        freq_type = re.sub(u"([^\u0041-\u007a])", "", freq)
        if freq_type == 'min':
            delta = (freq_n - 1) * 60 + 59
        elif freq_type == 'H':
            delta = (freq_n * 60 - 1) * 60 + 59
        else:
            raise ValueError

        morning_session_open = pd.Series(morning_session).apply(lambda x: x - _datetime.timedelta(seconds=delta))
        afternoon_session_open = pd.Series(afternoon_session).apply(lambda x: x - _datetime.timedelta(seconds=delta))
        morning_session_open.loc[0] = self.morning_open_time
        afternoon_session_open.loc[0] = self.afternoon_open_time

        self._open = pd.Series(list(morning_session_open) + list(afternoon_session_open), name='time')
        self._close = pd.Series(morning_session + afternoon_session, name='time')

        # self._open = self._open.apply(
        #     lambda x: "%s:%s:%s" % (str(x.hour).zfill(2), str(x.minute).zfill(2), str(x.second).zfill(2))
        # )
        # self._close = self._close.apply(
        #     lambda x: "%s:%s:%s" % (str(x.hour).zfill(2), str(x.minute).zfill(2), str(x.second).zfill(2))
        # )
        self._open = self._open.apply(
            lambda x: time(hour=x.hour, minute=x.minute, second=x.second, freq=self._freq, ignore=True)
        )
        self._close = self._close.apply(
            lambda x: time(hour=x.hour, minute=x.minute, second=x.second, freq=self._freq, ignore=True)
        )

    @staticmethod
    def time_range(start, end, freq='1min'):
        start = _datetime.datetime.combine(
            _datetime.date.today(),
            _datetime.time(hour=start.hour, minute=start.minute, second=start.second)
        )
        end = _datetime.datetime.combine(
            _datetime.date.today(),
            _datetime.time(hour=end.hour, minute=end.minute, second=end.second)
        )

        time_ranges = [
            _Time(i.time().hour, i.time().minute, i.time().second)
            for i in pd.date_range(start, end, freq=freq)
        ]

        if freq not in ('1min', '1s'):
            time_ranges = time_ranges[1:]
        return time_ranges

    @property
    def open(self) -> pd.Series:
        return self._open

    @property
    def close(self) -> pd.Series:
        return self._close

    @property
    def range(self) -> Tuple[pd.Series, pd.Series]:
        return self._open, self._close


class bardelta:
    """按bar位移"""

    def __init__(self, date_bars=0, time_bars=0, date_freq='D'):
        self._date_bars = date_bars
        self._time_bars = time_bars
        self._date_freq = date_freq

    def __repr__(self):
        args = []
        if self._date_bars:
            args.append("date_bars=%d" % self._date_bars)
        if self._time_bars:
            args.append("time_bars=%d" % self._time_bars)
        if self._date_bars and self._date_freq:
            args.append("date_freq='%s'" % self._date_freq)
        if not args:
            args.append('0')
        return "%s(%s)" % (self.__class__.__qualname__, ', '.join(args))

    __str__ = __repr__

    @property
    def date_bars(self):
        return self._date_bars

    @property
    def time_bars(self):
        return self._time_bars

    @property
    def date_freq(self) -> str:
        return self._date_freq

    def __eq__(self, other):
        if isinstance(other, bardelta):
            return self._cmp(other) == 0
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, bardelta):
            return self._cmp(other) <= 0
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, bardelta):
            return self._cmp(other) < 0
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, bardelta):
            return self._cmp(other) >= 0
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, bardelta):
            return self._cmp(other) > 0
        else:
            return NotImplemented

    def _cmp(self, other):
        assert isinstance(other, bardelta)
        if self.date_freq == other.date_freq:
            return _cmp(self._getstate(), other._getstate())
        else:
            raise ValueError(f'{self.date_freq} and {other.date_freq} inconsistent')

    def __bool__(self):
        return bool(self._date_bars or self._time_bars)

    def _getstate(self):
        return self._date_bars, self._time_bars

    def __add__(self, other):
        if self.date_freq == other.date_freq:
            if isinstance(other, bardelta):
                return bardelta(self.date_bars + other.date_bars, self.time_bars + other.time_bars)
            else:
                return NotImplemented
        else:
            raise ValueError(f'{self.date_freq} and {other.date_freq} inconsistent')

    def __sub__(self, other):
        if self.date_freq == other.date_freq:
            if isinstance(other, bardelta):
                return bardelta(self.date_bars - other.date_bars, self.time_bars - other.time_bars)
            else:
                return NotImplemented
        else:
            raise ValueError(f'{self.date_freq} and {other.date_freq} inconsistent')


class date:

    # Default Bar Type
    default_freqN: int = 1  # only support 1
    default_freqType: str = None  # 'D','W','M','Q','Y'

    # All Freq Bar Date Endpoint
    _D = _W = _M = _Q = _Y = None
    # To visit
    D: Calendar = None
    W: Calendar = None
    M: Calendar = None
    Q: Calendar = None
    Y: Calendar = None
    # All Calendar Dict
    calendar_open: Dict = None
    calendar_close: Dict = None
    calendar: Dict = None

    # Operation inverse
    operation_inverse = False  # 是否允许反向运算

    def __init__(self, year=None, month=None, day=None, pydate=None, freq=None, ignore=False):
        if pydate:
            pydate = pydate if isinstance(pydate, date) else _convert2date(pydate, freq)
            self._year = pydate.year
            self._month = pydate.month
            self._day = pydate.day
        elif year and month and day:
            self._year = year
            self._month = month
            self._day = day
        else:
            today = _datetime.date.today()
            self._year = today.year
            self._month = today.month
            self._day = today.day
        self._freq = freq if freq else self.default_freqType  # 如果没有设置频率，则使用默认频率
        self._ignore = ignore
        if not self._ignore and not self.validate(self._freq):  # 默认进行检查
            raise ValueError(f"{self} doesn't match freq {self._freq}")

    def __repr__(self):
        args = [
            "year=%d" % self._year,
            "month=%d" % self._month,
            "day=%d" % self._day,
            "freq='%s'" % self._freq,
        ]
        return "%s(%s)" % (self.__class__.__qualname__, ', '.join(args),)

    def __str__(self):
        return "%s-%s-%s" % (str(self._year).zfill(4),
                             str(self._month).zfill(2),
                             str(self._day).zfill(2)
                             )

    @property
    def year(self):
        return self._year

    @property
    def quarter(self):
        return int((self.month - 0.5) // 3 + 1)

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    @property
    def freq(self):
        return self._freq

    @property
    def ignore(self) -> bool:
        return self._ignore

    def index(self, freq: str = None):
        freq = freq if freq else self.freq
        if self.validate(freq):
            return self.calendar[freq].values.tolist().index(self)
        else:
            raise ValueError(f"{self} is not in freq '{freq}'")

    def validate(self, freq: str = None):
        """验证是否符合该频率"""
        freq = freq if freq else self.freq
        return self in self.calendar[freq].values

    def open(self, freq: str = None, if_break: str = None) -> 'date':
        """必须是交易日"""
        freq = freq if freq else self.freq
        if self.is_trading(self):
            i = bisect.bisect_left(self.calendar[freq], self)
            return self.calendar_open[freq].loc[i]
        else:
            return self.close(freq, if_break).open(freq, if_break)

    def close(self, freq: str = None, if_break: str = None) -> 'date':
        """必须是交易日，如果不是交易日基于剔除未来函数的原则，寻找历史最近的一个交易日"""
        assert if_break in ['past', 'future', None], "if_break can only be 'past', 'future' or None"
        freq = freq if freq else self.freq
        if self.is_trading(self):
            i = bisect.bisect_left(self.calendar[freq], self)
            return self.calendar_close[freq].loc[i]

        # 区分属于哪种非交易日：（1）时间段内非交易日；（2）时间段间非交易日
        else:
            break_type = self.break_type(self, freq)

        if break_type == "internal break":
            if if_break == 'past':
                # 自动迭代
                return self.nearest(if_break='past').close(freq, if_break) - 1

            elif if_break == 'future':
                return self.nearest(if_break='past').close(freq, if_break) + 1  # 注意if_break不同

            else:
                return self.nearest(if_break='past').close(freq, if_break)

        elif break_type == "external break":
            if if_break == 'past':
                return self.nearest(if_break).close(freq, if_break)

            elif if_break == 'future':
                return self.nearest(if_break).close(freq, if_break)

            else:
                # 交易段间的非交易日，一定要指定if_break
                raise ValueError("The date is external break, missing param if_break.")

        else:
            raise ValueError("Break type error")

    def range(self, freq: str = None, if_break: str = None):
        return self.open(freq, if_break), self.close(freq, if_break)

    def is_open(self, freq: str = None):
        return self == self.open(freq)

    def is_close(self, freq: str = None):
        return self == self.close(freq)

    def py_date(self):
        """transfer to python datetime.date"""
        return _datetime.date(year=self.year, month=self.month, day=self.day)

    def pd_date(self):
        """transfer to python.pandas datetime"""
        return pd.to_datetime([self.py_date()])

    def nearest(self, if_break: str = None):
        if self.is_break(self):
            if if_break == 'past':
                return (self - _datetime.timedelta(days=1)).nearest(if_break)
            elif if_break == 'future':
                return (self + _datetime.timedelta(days=1)).nearest(if_break)
            else:
                raise ValueError("The date is break, missing param if_break.")
        else:
            return self

    def __eq__(self, other):
        other = other if isinstance(other, date) else _convert2date(other)

        if isinstance(other, date):
            return self._cmp(other) == 0
        else:
            return NotImplemented

    def __le__(self, other):
        other = other if isinstance(other, date) else _convert2date(other)

        if isinstance(other, date):
            return self._cmp(other) <= 0
        else:
            return NotImplemented

    def __lt__(self, other):
        other = other if isinstance(other, date) else _convert2date(other)

        if isinstance(other, date):
            return self._cmp(other) < 0
        else:
            return NotImplemented

    def __ge__(self, other):
        other = other if isinstance(other, date) else _convert2date(other)

        if isinstance(other, date):
            return self._cmp(other) >= 0
        else:
            return NotImplemented

    def __gt__(self, other):
        other = other if isinstance(other, date) else _convert2date(other)

        if isinstance(other, date):
            return self._cmp(other) > 0
        else:
            return NotImplemented

    def _cmp(self, other):
        assert isinstance(other, date)
        return _cmp(self._getstate(), other._getstate())

    def __bool__(self):
        return bool(self.year or self.month or self.day)

    def _getstate(self):
        return self.year, self.month, self.day

    def __add__(self, other):
        if isinstance(other, int):
            other = bardelta(date_bars=other, date_freq=self.freq)
        if isinstance(other, bardelta):
            return self.calendar[other.date_freq].loc[
                (self.index(other.date_freq) + other.date_bars) % len(self.calendar[other.date_freq])]
        elif isinstance(other, _datetime.timedelta):
            s = _datetime.date(self.year, self.month, self.day) + other
            return date(s.year, s.month, s.day, freq=self.freq, ignore=True)
        else:
            return NotImplemented

    def __sub__(self, other):
        """和datetime.timedelta操作无需交易日"""
        if isinstance(other, int):
            other = bardelta(date_bars=other, date_freq=self.freq)
        if isinstance(other, bardelta):
            return self.calendar[other.date_freq].loc[
                (self.index(other.date_freq) - other.date_bars) % len(self.calendar[other.date_freq])]
        elif isinstance(other, _datetime.timedelta):
            s = _datetime.date(self.year, self.month, self.day) - other
            return date(s.year, s.month, s.day, freq=self.freq, ignore=True)
        elif isinstance(other, date):
            assert self.freq == other.freq, f"{self.freq} and {other.freq} inconsistent"
            return bardelta(date_bars=self.index() - other.index(), date_freq=self.freq)
        else:
            return NotImplemented

    def __radd__(self, other):
        if self.operation_inverse:
            return self + other
        else:
            raise NotImplementedError("Use: tradetime.date.operation_inverse = True")

    def __rsub__(self, other):
        if self.operation_inverse:
            return self - other
        else:
            raise NotImplementedError("Use: tradetime.date.operation_inverse = True")

    @classmethod
    def bars(cls, start_date, end_date, freq=None, is_open=False, overflow=False) -> pd.Series:
        freq = freq if freq else cls.default_freqType
        start_date = start_date if isinstance(start_date, date) else _convert2date(start_date, freq)
        end_date = end_date if isinstance(end_date, date) else _convert2date(end_date, freq)

        if cls.break_type(start_date, freq) == "internal break":
            start_id = start_date.close(freq, if_break=None).index(freq)
        else:
            start_id = start_date.close(freq, if_break='future').index(freq)

        end_id = end_date.close(freq, if_break='past').index(freq)
        if cls.calendar[freq].loc[end_id] > end_date and not overflow:  # 可能溢出
            end_id -= 1
        if not is_open:
            return cls.calendar[freq].loc[start_id: end_id].reset_index(drop=True)
        else:
            return cls.calendar_open[freq].loc[start_id: end_id].reset_index(drop=True)

    @classmethod
    def quarter_range(cls, start_date, end_date, type_: type = None, fmt: str = None, **kw_bars):
        """获取季度日期，fmt设置返回格式"""
        result = cls.bars(start_date, end_date, freq='Q', **kw_bars)
        if type_ == str:
            fmt = fmt if fmt else "(y)Q(q)"
            return result.apply(
                lambda x: fmt.replace(
                    "(y)", str(x.year)
                ).replace(
                    "(q)", str(x.quarter)
                ))
        else:
            return result

    @classmethod
    def current(cls, freq=None, if_break: str = None):
        """当前所处bar"""
        freq = freq if freq else cls.default_freqType
        now_date = _convert2date(_datetime.date.today(), freq)  # ignore=True
        return now_date.close(if_break=if_break)

    @classmethod
    def future(cls, n=1, freq=None):
        freq = freq if freq else cls.default_freqType
        return cls.current(freq) + bardelta(date_bars=n, date_freq=freq)

    @classmethod
    def previous(cls, n=1, freq=None):
        freq = freq if freq else cls.default_freqType
        return cls.current(freq) - bardelta(date_bars=n, date_freq=freq)

    @classmethod
    def is_trading(cls, d=None):
        if d is None:  # 没有传入日期，则默认今天
            d = _datetime.date.today()
        if isinstance(d, _datetime_type):
            d = _convert2date(d)
        assert isinstance(d, date)
        return d in cls.calendar_close['D'].values.tolist()

    @classmethod
    def is_break(cls, d=None):
        return not cls.is_trading(d)

    @classmethod
    def break_type(cls, d=None, freq='D'):
        """非交易日类型，internal break or external break"""
        d = d if isinstance(d, date) else _convert2date(d)

        if cls.is_break(d):
            d_past = d_future = d
            while cls.is_break(d_past):
                d_past = d_past - _datetime.timedelta(days=1)
            while cls.is_break(d_future):
                d_future = d_future + _datetime.timedelta(days=1)
            # 先确保是交易日
            if d_past.close(freq) == d_future.close(freq):
                return "internal break"
            else:
                return "external break"
        else:
            return

    @classmethod
    def get_close(cls, year=None, q=None, m=None):
        """返回第几年某频率第n个交易交易open日期"""
        year = year if year else _datetime.date.today().year
        assert bool(q) + bool(m) == 1, "q or m"
        freq = 'M' if m else 'Q'
        m = m if m else q * 3
        d = cls(year, m, _calendar.monthrange(year, m)[-1], freq=freq, ignore=True)
        while not cls.is_trading(d):
            d = d - _datetime.timedelta(days=1)
        return d

    @classmethod
    def get_open(cls, year=None, q=None, m=None):
        return cls.get_close(year, q, m).open()

    @classmethod
    def set_option(cls, default_freq: str = 'D'):
        cls.default_freqType = default_freq

        if cls._D is None:
            cls._D = cls.D = Calendar('D')
            cls._W = cls.W = Calendar('W')
            cls._M = cls.M = Calendar('M')
            cls._Q = cls.Q = Calendar('Q')
            cls._Y = cls.Y = Calendar('Y')
            # All Calendar Dict
            cls.calendar_open = dict(
                zip(list('DWMQY'), [cls._D.open, cls._W.open, cls._M.open, cls._Q.open, cls._Y.open]))
            cls.calendar_close = dict(
                zip(list('DWMQY'), [cls._D.close, cls._W.close, cls._M.close, cls._Q.close, cls._Y.close]))
            cls.calendar = cls.calendar_close


class time:
    """
    ignore: 可以生成和频率不匹配的time实例
    """
    # Default Bar Type
    default_freq: str = None  # 5min
    default_freqN: int = None  # 5
    default_freqType: str = None  # min

    # Session To visit
    # _1s: Session = None
    _3s: Session = None
    _1m: Session = None
    _5m: Session = None
    _15m: Session = None
    _30m: Session = None
    _1h: Session = None
    # All Session Dict
    session_open: Dict = None
    session_close: Dict = None
    session: Dict = None

    # 是否允许逆运算
    operation_inverse = False

    def __init__(self,
                 hour: int = None,
                 minute: int = None,
                 second: int = None,
                 pytime: _AnyDatetime_Type = None,
                 freq: str = None,
                 ignore: bool = False):

        if pytime:
            pytime = pytime if isinstance(pytime, time) else _convert2time(pytime, freq)
            self._hour = pytime.hour
            self._minute = pytime.minute
            self._second = pytime.second
        elif hour or minute or second:
            self._hour = hour if hour else 0
            self._minute = minute if minute else 0
            self._second = second if second else 0
        else:
            today = _datetime.datetime.now().time()
            self._hour = today.hour
            self._minute = today.minute
            self._second = today.second
        if self.default_freqType in ('min', 'T') and not ignore:
            self._second = 0

        self._freq = freq if freq else self.default_freq  # 如果没有设置频率，则使用默认频率
        self._ignore = ignore
        if not self._ignore and not self.validate(self._freq):  # 默认进行检查
            raise ValueError(f"{self} doesn't match freq {self._freq}")

    def __repr__(self):
        args = [
            "hour=%d" % self._hour,
            "minute=%d" % self._minute,
            "second=%d" % self._second,
            "freq='%s'" % self._freq,
            # "bar=%s" % self.session.index(self)  # 不可展示
        ]
        return "%s(%s)" % (self.__class__.__qualname__, ', '.join(args),)

    def __str__(self):
        return "%s:%s:%s" % (str(self._hour).zfill(2),
                             str(self._minute).zfill(2),
                             str(self._second).zfill(2)
                             )

    @property
    def hour(self) -> int:
        if self._hour:
            return self._hour
        else:
            return 0

    @property
    def minute(self) -> int:
        if self._minute:
            return self._minute
        else:
            return 0

    @property
    def second(self) -> int:
        if self._second:
            return self._second
        else:
            return 0

    @property
    def freq_n(self) -> int:
        """5min -> 5"""
        return int(re.sub(u"([^\u0030-\u0039])", "", self._freq))

    @property
    def freq_type(self) -> str:
        """5min -> min"""
        return re.sub(u"([^\u0041-\u007a])", "", self._freq)

    @property
    def freq(self):
        """5min"""
        return self._freq

    @property
    def ignore(self) -> bool:
        return self._ignore

    def index(self, freq: str = None) -> int:
        freq = freq if freq else self._freq
        if self.validate(freq):
            return self.session[freq].values.tolist().index(self)
        else:
            raise ValueError(f"{self} is not in freq '{freq}'")

    def validate(self, freq: str = None) -> bool:
        """time实例是否合法"""
        freq = freq if freq else self._freq
        return self in self.session[freq].values

    def open(self, freq: str = None) -> 'time':
        freq = freq if freq else self._freq
        i = bisect.bisect_left(self.session[freq], self)
        return self.session_open[freq].loc[i]

    def close(self, freq: str = None) -> 'time':
        freq = freq if freq else self.freq
        i = bisect.bisect_left(self.session[freq], self)
        return self.session_close[freq].loc[i]

    def range(self, freq: str = None) -> Tuple['time', 'time']:
        return self.open(freq), self.close(freq)

    def py_time(self):
        return _datetime.time(self.hour, self.minute, self.second)

    def str(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, _datetime_type):
            other = _datetime2time(other)
        if isinstance(other, time):
            return self._cmp(other) == 0
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, _datetime_type):
            other = _datetime2time(other)
        if isinstance(other, time):
            return self._cmp(other) <= 0
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, _datetime_type):
            other = _datetime2time(other)
        if isinstance(other, time):
            return self._cmp(other) < 0
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, _datetime_type):
            other = _datetime2time(other)
        if isinstance(other, time):
            return self._cmp(other) >= 0
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, _datetime_type):
            other = _datetime2time(other)
        if isinstance(other, time):
            return self._cmp(other) > 0
        else:
            return NotImplemented

    def _cmp(self, other):
        assert isinstance(other, time)
        return _cmp(self._getstate(), other._getstate())

    def __bool__(self):
        return bool(self.hour or self.minute or self.second)

    def _getstate(self):
        return self.hour, self.minute, self.second

    def __add__(self, other, ignore=True) -> 'time':
        if isinstance(other, int):
            other = bardelta(time_bars=other)
        if isinstance(other, bardelta):
            return self.session[self.freq].loc[(self.index(freq=self.freq) + other.time_bars) % len(self.session[self.freq])]
        elif isinstance(other, _datetime.timedelta):
            s = _datetime.datetime.combine(
                _datetime.date.today(),
                _datetime.time(self.hour, self.minute, self.second)
            ) + other
            return time(s.hour, s.minute, s.second, ignore=ignore)
        else:
            return NotImplemented

    def __sub__(self, other, ignore=True) -> 'time':
        if isinstance(other, int):
            other = bardelta(time_bars=other)
        if isinstance(other, bardelta):
            return self.session[self.freq].loc[(self.index(freq=self.freq) - other.time_bars) % len(self.session[self.freq])]
        elif isinstance(other, _datetime.timedelta):
            s = _datetime.datetime.combine(
                _datetime.date.today(),
                _datetime.time(self.hour, self.minute, self.second)
            ) - other
            return time(s.hour, s.minute, s.second, ignore=ignore)
        else:
            return NotImplemented

    # def __radd__(self, other):
    #     if isinstance(other, (int, bardelta, _datetime.timedelta)):
    #         return self + other
    #     else:
    #         return NotImplemented
    #
    # def __rsub__(self, other):
    #     if isinstance(other, (int, bardelta, _datetime.timedelta)):
    #         return self - other
    #     else:
    #         return NotImplemented

    def __radd__(self, other):
        if self.operation_inverse:
            return self + other
        else:
            raise NotImplementedError("Use: tradetime.time.operation_inverse = True")

    def __rsub__(self, other):
        if self.operation_inverse:
            return self - other
        else:
            raise NotImplementedError("Use: tradetime.time.operation_inverse = True")

    @classmethod
    def bars(cls, start_time, end_time, freq=None, is_open=False, overflow=False) -> pd.Series:
        freq = freq if freq else cls.default_freq

        start_time = start_time if isinstance(start_time, time) else _convert2time(start_time, freq)
        end_time = end_time if isinstance(end_time, time) else _convert2time(end_time, freq)

        start_id = start_time.close(freq).index(freq)
        end_id = end_time.close(freq).index(freq)

        if cls.session_close[freq].loc[end_id] > end_time and not overflow:  # 可能溢出
            end_id -= 1

        if not is_open:
            return cls.session_close[freq].loc[start_id: end_id].reset_index(drop=True)
        else:
            return cls.session_open[freq].loc[start_id: end_id].reset_index(drop=True)

    @classmethod
    def current(cls, freq=None, if_break=None) -> 'time':
        freq = freq if freq else cls.default_freq
        now_dt = _datetime.datetime.now()
        now_dt = _datetime.datetime(2022, 6, 13, 12)
        now = time(now_dt.hour, now_dt.minute, now_dt.second, freq=freq, ignore=True)
        i = bisect.bisect_left(cls.session[freq], now)
        if cls.is_trading(now_dt) or if_break == 'future':
            return cls.session_close[freq].loc[i]
        else:
            assert if_break == 'past'
            return cls.session_close[freq].loc[i - 1]

    @classmethod
    def future(cls, n=1) -> 'time':
        current = cls.current()
        if current:
            return current + bardelta(time_bars=n)
        else:
            return NotImplemented

    @classmethod
    def previous(cls, n=1) -> 'time':
        current = cls.current()
        if current:
            return current - bardelta(time_bars=n)
        else:
            return NotImplemented

    @classmethod
    def is_trading(cls, t=None) -> bool:
        if t is None:  # 没有传入时间，则默认现在
            t = _datetime.datetime.now()
        if isinstance(t, _anydatetime_type):
            t = _convert2time(t)
        assert isinstance(t, time), f'Error Type {t.__class__}'
        return any([
            Session.morning_open_time <= t.py_time() <= Session.morning_close_time,
            Session.afternoon_open_time <= t.py_time() <= Session.afternoon_close_time
        ])

    @classmethod
    def is_break(cls, t=None) -> bool:
        return not cls.is_trading(t)

    @classmethod
    def break_type(cls, t=None) -> str:
        if cls.is_break(t):
            if t is None:  # 没有传入时间，则默认现在
                t = _datetime.datetime.now()
            if isinstance(t, _anydatetime_type):
                t = _convert2time(t)
            assert isinstance(t, time)
            if t < Session.morning_open_time or t.py_time() > Session.afternoon_close_time:
                return 'external break'
            if Session.morning_close_time < t.py_time() < Session.afternoon_open_time:
                return 'internal break'

    @classmethod
    def set_option(cls, default_freq='1min', include=True):

        _check_time_freq(default_freq)
        cls.default_freq = default_freq
        cls.default_freqN = int(re.sub(u"([^\u0030-\u0039])", "", default_freq))
        cls.default_freqType = re.sub(u"([^\u0041-\u007a])", "", default_freq)

        Session.include = include

        # cls._1s = Session('1s')
        cls._1m = Session('1min')
        cls._5m = Session('5min')
        cls._15m = Session('15min')
        cls._30m = Session('30min')
        cls._1h = Session('1H')

        # All Session Dict
        freq_list = [
            # '1s',
            '1min', '5min', '15min', '30min', '1H']
        cls.session_open = dict(
            zip(freq_list, [
                # cls._1s.open,
                cls._1m.open, cls._5m.open, cls._15m.open, cls._30m.open, cls._1h.open]))
        cls.session_close = dict(
            zip(freq_list, [
                # cls._1s.close,
                cls._1m.close, cls._5m.close, cls._15m.close, cls._30m.close, cls._1h.close]))
        cls.session = cls.session_close


class datetime(date):
    ...


# Other Functions
...


# Settings
def set_date(default_freq: str = 'D'):
    date.set_option(default_freq)


def set_time(default_freq: str = '1min', include=True):
    """默认为241分钟的一分钟bar"""
    time.set_option(default_freq, include)


def set_operation_inverse(inverse=False):
    """是否允许逆向运算，默认不可以"""
    date.operation_inverse = inverse
    time.operation_inverse = inverse


# Update
def update():
    """Update Tradetime from SandInvest"""
    import sandinvest as si
    calendar = si.get_calendar(date="all")
    calendar.to_csv(os.path.join(__packagePath__, 'data.csv'), index=False)
    print(f"[{_datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] @ TradeTime is updated.")


# Default Settings
set_date()
set_time()
set_operation_inverse()