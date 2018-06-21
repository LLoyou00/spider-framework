import six
from framework.http.request import Request


def request_to_dict(request, spider):
    cb = request.callback
    if callable(cb):
        cb = _find_method(spider, cb)

    return {
        'url': request.url,
        'callback': cb,
    }


def request_from_dict(d, spider):
    cb = d['callback']
    if cb and spider:
        cb = _get_method(spider, cb)

    return Request(d['url'], cb)


def _find_method(obj, func):
    if obj:
        try:
            func_self = six.get_method_self(func)
        except AttributeError:
            pass
        else:
            if func_self is obj:
                return six.get_method_function(func).__name__
    raise ValueError("Function %s is not a method of: %s" % (func, obj))


def _get_method(obj, name):
    name = str(name)
    try:
        return getattr(obj, name)
    except AttributeError:
        raise ValueError("Method %r not found in: %s" % (name, obj))
