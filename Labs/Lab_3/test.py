def wrap(pre):
    def decorate(func):
        def call(*args, **kwargs):
            pre(func, *args, **kwargs)
            result = func(*args, **kwargs)

            return result

        return call

    return decorate


def trace_in(func, *args, **kwargs):
    print("Entering function", func.__name__)
    func.


def trace_out(func, *args, **kwargs):
    print("Leaving function", func.__name__)


@wrap(trace_in)
def calc(x, y):
    return x + y


if __name__ == '__main__':
    print(calc(1, 2))
