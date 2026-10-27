"""Focused observations against the retained upstream sources; not a benchmark."""
import sys
import platform
import runpy
from pathlib import Path
root = Path(__file__).parent / 'upstream'
sys.path.insert(0, str(root))
from boltons.queueutils import PriorityQueue, HeapPriorityQueue, SortedPriorityQueue, _REMOVED
print('Python:', platform.python_version(), platform.python_implementation())
print('module:', sys.modules['boltons.queueutils'].__file__)
tests = runpy.run_path(str(root / 'tests/test_queueutils.py'))
tests['test_heap_queue']()
tests['test_sorted_queue']()
print('Upstream test functions directly invoked: 2 passed (pytest unavailable)')
print('PriorityQueue alias:', PriorityQueue.__name__)
def snapshot(q):
    return {'live': len(q), 'physical': len(q._pq), 'entries': [[p,c,'REMOVED' if t is _REMOVED else t] for p,c,t in q._pq]}
for cls in (HeapPriorityQueue, SortedPriorityQueue):
    q = cls()
    print('\nBackend:', cls.__name__, type(q._pq).__name__)
    for task, p in [('A', 1), ('B', 3), ('C', 3)]:
        q.add(task, p)
        print('add', task, p, snapshot(q))
    print('peek:', q.peek(), snapshot(q))
    print('pop:', q.pop(), snapshot(q))
    q.add('A', 3)
    print('update A to 3:', snapshot(q))
    q.remove('C')
    print('remove C:', snapshot(q))
    print('peek after cull:', q.peek(), snapshot(q))
    print('pop A:', q.pop(), snapshot(q))
    print('empty default:', q.pop(None), snapshot(q))
    for method, args in [('remove', ('missing',)), ('peek', ()), ('pop', ()), ('add', ([], 1))]:
        try:
            getattr(q, method)(*args)
        except Exception as e:
            print('boundary:', method, type(e).__name__, str(e))
    q.add('stable', 2)
    try:
        q.add('stable', 'bad')
    except ValueError:
        print('failed conversion retains old task:', q.peek(), snapshot(q))
    q2 = cls(priority_key=lambda p: p)
    q2.add('low', 1)
    q2.add('high', 2)
    print('identity priority_key pop:', q2.pop())
    q3 = cls()
    q3.add('large', 9007199254740993)
    q3.add('larger', 9007199254740994)
    print('float normalized:', snapshot(q3))
