"""A tiny call tracer: decorate classes with @traced, run client code inside `with trace() as t:`,
then t.diagram() draws the sequence diagram of what actually happened."""
import functools
from .diagrams import sequence_diagram

_active = None


def _short(x, limit=14):
    if isinstance(x, str):
        s = repr(x)
    elif isinstance(x, (int, float, bool, type(None))):
        s = repr(x)
    elif isinstance(x, (list, tuple, dict, set)):
        s = f"{type(x).__name__}[{len(x)}]"
    else:
        s = participant_name(x)
    return s if len(s) <= limit else s[:limit - 2] + ".."


def _plain_attr(obj, attr):
    # Read an attribute without triggering __getattr__ (proxies forward it, and may not be initialised yet).
    try:
        d = vars(obj)
    except TypeError:
        d = {}
    if attr in d:
        return d[attr]
    return getattr(type(obj), attr, None)


def participant_name(obj):
    tn = _plain_attr(obj, "trace_name")
    if isinstance(tn, str):
        return tn
    cls = type(obj).__name__
    name = _plain_attr(obj, "name")
    if isinstance(name, str) and name:
        return f"{cls}({name})"
    return cls


class Tracer:
    def __init__(self, returns=False):
        self.records = []          # [caller, callee, label, kind]
        self.stack = ["Client"]
        self.returns = returns

    def __enter__(self):
        global _active
        _active = self
        self.records = []
        self.stack = ["Client"]
        return self

    def __exit__(self, *exc):
        global _active
        _active = None
        return False

    def participants(self):
        seen = []
        for caller, callee, _l, _k in self.records:
            for p in (caller, callee):
                if p not in seen:
                    seen.append(p)
        return seen

    def diagram(self, title="", max_messages=40, figsize=None):
        msgs = [tuple(r) for r in self.records[:max_messages]]
        if len(self.records) > max_messages:
            msgs.append(("Client", "Client", f"... {len(self.records) - max_messages} more", "call"))
        return sequence_diagram(self.participants(), msgs, title=title, figsize=figsize)

    def text(self):
        return "\n".join(f"{'  ' * 0}{caller} -> {callee}: {label}" for caller, callee, label, kind in self.records if kind == "call")


def trace(returns=False):
    return Tracer(returns=returns)


def traced(cls):
    # Wrap every plain method defined on the class (including __init__) so calls are recorded.
    for name, attr in list(cls.__dict__.items()):
        if not callable(attr) or isinstance(attr, (staticmethod, classmethod)):
            continue
        if name.startswith("__") and name != "__init__":
            continue
        setattr(cls, name, _wrap(attr, name))
    return cls


def _wrap(fn, name):
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        tracer = _active
        if tracer is None:
            return fn(self, *args, **kwargs)
        arg_text = ", ".join([_short(a) for a in args] + [f"{k}={_short(v)}" for k, v in kwargs.items()])
        label = f"new {type(self).__name__}({arg_text})" if name == "__init__" else f"{name}({arg_text})"
        record = [tracer.stack[-1], participant_name(self) if name != "__init__" else type(self).__name__, label, "call"]
        tracer.records.append(record)
        tracer.stack.append(record[1])
        try:
            result = fn(self, *args, **kwargs)
        finally:
            tracer.stack.pop()
        if name == "__init__":
            record[1] = participant_name(self)          # the name may only exist after __init__ ran
        if tracer.returns and name != "__init__":
            tracer.records.append([record[1], record[0], f"return {_short(result)}", "return"])
        return result
    return wrapper
