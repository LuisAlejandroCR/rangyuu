import pytest
from rangyuu.provider import HttpProvider
def test_plan_limits_and_secret_not_repr():
 p=HttpProvider(token="SECRET").plan("build",["a.py"]); assert p.files==("a.py",)
 try: HttpProvider().plan("x"*2001)
 except ValueError: pass
 else: assert False
 assert "SECRET" not in repr(HttpProvider(token="SECRET"))
