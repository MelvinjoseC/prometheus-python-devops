import functools
import inspect
from timeit import default_timer
from types import TracebackType
from typing import (
    Any, Callable, Literal, Optional, Tuple, Type, TYPE_CHECKING, TypeVar,
    Union,
)

from .decorator import decorate

if TYPE_CHECKING:
    from . import Counter
    F = TypeVar("F", bound=Callable[..., Any])


class ExceptionCounter:
    def __init__(self, counter: "Counter", exception: Union[Type[BaseException], Tuple[Type[BaseException], ...]]) -> None:
        self._counter = counter
        self._exception = exception

    def __enter__(self) -> None:
        pass

    def __exit__(self, typ: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]) -> Literal[False]:
        if isinstance(value, self._exception):
            self._counter.inc()
        return False

    def __call__(self, f: "F") -> "F":
        if inspect.iscoroutinefunction(f) or (
            hasattr(f, '__call__') and inspect.iscoroutinefunction(f.__call__)
        ):
            @functools.wraps(f)
            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return await f(*args, **kwargs)
            return async_wrapped  # type: ignore

        def wrapped(func, *args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorate(f, wrapped)


class InprogressTracker:
    def __init__(self, gauge):
        self._gauge = gauge

    def __enter__(self):
        self._gauge.inc()

    def __exit__(self, typ, value, traceback):
        self._gauge.dec()

    def __call__(self, f: "F") -> "F":
        if inspect.iscoroutinefunction(f) or (
            hasattr(f, '__call__') and inspect.iscoroutinefunction(f.__call__)
        ):
            @functools.wraps(f)
            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return await f(*args, **kwargs)
            return async_wrapped  # type: ignore

        def wrapped(func, *args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorate(f, wrapped)


class Timer:
    def __init__(self, metric, callback_name):
        self._metric = metric
        self._callback_name = callback_name
        self.duration = None

    def _new_timer(self):
        return self.__class__(self._metric, self._callback_name)

    def __enter__(self):
        self._start = default_timer()
        return self

    def __exit__(self, typ, value, traceback):
        # Time can go backwards.
        self.duration = max(default_timer() - self._start, 0)
        callback = getattr(self._metric, self._callback_name)
        callback(self.duration)

    def labels(self, *args, **kw):
        self._metric = self._metric.labels(*args, **kw)

    def __call__(self, f: "F") -> "F":
        if inspect.iscoroutinefunction(f) or (
            hasattr(f, '__call__') and inspect.iscoroutinefunction(f.__call__)
        ):
            @functools.wraps(f)
            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
                with self._new_timer():
                    return await f(*args, **kwargs)
            return async_wrapped  # type: ignore

        def wrapped(func, *args, **kwargs):
            # Obtaining new instance of timer every time
            # ensures thread safety and reentrancy.
            with self._new_timer():
                return func(*args, **kwargs)

        return decorate(f, wrapped)
