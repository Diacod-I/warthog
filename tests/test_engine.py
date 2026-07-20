from mag_py import engine


def test_add():
    a = engine.Value(2.0)
    b = engine.Value(3.0)
    c = a + b
    assert c.data == 5.0


def test_add_plain_number_left():
    # int + Value -> int's __add__ returns NotImplemented,
    # Python fallbacks to our __radd__
    b = 1 + engine.Value(2.0)
    assert b.data == 3.0


def test_add_plain_number_right():
    # Value + int -> __add__ wraps the int
    b = engine.Value(2.0) + 1
    assert b.data == 3.0


def test_mul():
    a = engine.Value(5.0)
    b = engine.Value(3.0)
    c = a * b
    assert c.data == 15.0


def test_mul_plain_number_both_sides():
    assert (engine.Value(5.0) * 2).data == 10.0
    assert (2 * engine.Value(5.0)).data == 10.0


def test_graph_records_parents():
    a = engine.Value(2.0)
    b = engine.Value(3.0)
    c = a + b
    assert c._prev == {a, b}
    assert c._op == "+"


def test_expression_build_chain():
    a = engine.Value(2.0)
    b = engine.Value(-3.0)
    c = engine.Value(15.0)
    d = a * b + c
    # d's parents are c and the anonymous intermediate (a*b)
    assert len(d._prev) == 2
    assert c in d._prev
    # find the intermediate and check its parents
    (inter,) = d._prev - {c}
    assert inter.data == -6.0
    assert inter._prev == {a, b}


def test_wrapped_number_becomes_graph_node():
    a = engine.Value(2.0)
    c = a + 1
    # the int gets promoted to Value and recorded as a parent
    assert len(c._prev) == 2
    (wrapped,) = c._prev - {a}
    assert wrapped.data == 1
    assert wrapped._prev == set()
    assert wrapped._op == ""


def test_mixed_expression():
    # natural math syntax over values
    x = engine.Value(3.0)
    y = 2 * x + 10
    assert y.data == 16.0
