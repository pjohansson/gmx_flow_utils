import io
import itertools

from gmx_flow.utils.fileio import loop_items


def test_loop_items_yields_from_lists():
    items = ['one', 'two', 'three']
    yielded = list(loop_items(items))
    assert items == yielded


def test_loop_items_yields_from_iterators():
    yielded = list(loop_items(range(10)))
    assert yielded == [i for i in range(10)]


def test_loop_items_yields_from_generators():
    def gen(n):
        i = 0
        while i < n:
            yield i
            i += 1

    yielded = list(loop_items(gen(10)))
    assert yielded == [i for i in range(10)]


def test_loop_items_writes_indexing_into_fp():
    items = ['one', 'two', 'three']

    buf = io.StringIO("")
    list(loop_items(items, fp=buf))

    contents = buf.getvalue()
    assert contents == "\r(1/3) \r(2/3) \r(3/3) \n"


def test_loop_items_formatted_indexing_uses_fixed_format_from_largest_index():
    items = [i for i in range(10)]

    buf = io.StringIO("")
    yielded = list(loop_items(items, fp=buf))

    contents = buf.getvalue()

    # With 10 items we expect indices to be ( 1/10), ( 2/10), ..., (10/10)
    # Width = 2!
    expected = ' '.join(
        [f"\r({i + 1:2}/10)" for i, _ in enumerate(yielded)] + ['\n'])

    assert contents == expected


def test_loop_items_with_quiet_writes_nothing_to_buffer():
    items = [i for i in range(10)]

    buf = io.StringIO("")
    yielded = list(loop_items(items, fp=buf, quiet=True))

    contents = buf.getvalue()
    assert contents == ""


def test_loop_items_caps_at_500k_items():
    num_max = 500_000
    items = list(range(2 * num_max))
    yielded = list(loop_items(items))

    assert len(yielded) == num_max
    assert yielded == items[:num_max]
