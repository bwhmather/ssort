import functools
import sys
import weakref

if sys.version_info < (3, 9):
    memoize = functools.lru_cache(maxsize=None)
else:
    memoize = functools.cache

_memoize_weak_cache = weakref.WeakKeyDictionary()


def memoize_weak(fn):
    @functools.wraps(fn)
    def _wrapper(target, *args, **kwargs):
        # We need to avoid doing more than one read from each WeakKeyDict in
        # case our argument is not the same instance as the key in the cache.
        # Using this decorator for arguments or callables with value semantics
        # is a little pointless, but that's no excuse for blowing up.
        try:
            fn_cache = _memoize_weak_cache[fn]
        except KeyError:
            fn_cache = weakref.WeakKeyDictionary()
            _memoize_weak_cache[fn] = fn_cache

        try:
            closure = fn_cache[target]
        except KeyError:
            closure = memoize(
                lambda *args, **kwargs: fn(target, *args, **kwargs)
            )
            fn_cache[target] = closure

        return closure(*args, **kwargs)

    return _wrapper


def sort_key_from_iter(values):
    index = {statement: index for index, statement in enumerate(values)}
    key = lambda value: index[value]
    return key
