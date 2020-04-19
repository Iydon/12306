__all__ = ('lazy_property', )


def lazy_property(func):
    '''Lazy property

    References
    =======
    (Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p10_using_lazily_computed_properties.html]

    Example
    =======
        >>> import math
        >>> class Circle:
        ... 	def __init__(self, radius):
        ... 		self.radius = radius
        ... 	@lazy_property
        ... 	def area(self):
        ... 		print('Computing area')
        ... 		return math.pi * self.radius**2
    '''
    name = '_lazy_' + func.__name__
    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy
