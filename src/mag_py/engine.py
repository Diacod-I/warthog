from __future__ import annotations


class Value:
    def __init__(self, data, _children=(), _op=""):
        self.data = data
        self._prev = set(_children)  # the Values this one was computed from
        self._op = _op  # the operation that produced it ('' = a leaf in the compute graph)

    def __repr__(self) -> str:
        return f"Value(data={self.data})"

    def __add__(self, other) -> Value:
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")
        return out

    def __radd__(self, other) -> Value:
        return self + other

    def __mul__(self, other) -> Value:
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")
        return out

    def __rmul__(self, other) -> Value:
        return self * other
