from __future__ import annotations

import typing
from typing import Any


def f_posonly(posonly, /):
    ...


def f_posonly_default(posonly=0, /):
    ...


def f_posonly_poskw(posonly, /, poskw):
    ...


def f_posonly_poskw_default(posonly, /, poskw=0):
    ...


def f_posonly_default_poskw_default(posonly=0, /, poskw=1):
    ...


def f_posonly_poskw_kwonly(posonly, /, poskw, *, kwonly):
    ...


def f_posonly_poskw_kwonly_default(posonly, /, poskw, *, kwonly=0):
    ...


def f_posonly_poskw_default_kwonly_default(posonly, /, poskw=0, *, kwonly=1):
    ...


def f_posonly_default_poskw_default_kwonly_default(posonly=0, /, poskw=1, *, kwonly=2):
    ...


def f_var(*args: str, kw=1, **kwargs: int):
    ...


def f_annorations(a: str, b: Any, c: typing.Optional[typing.List[int]], d: float | None):
    ...
