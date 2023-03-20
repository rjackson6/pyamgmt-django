"""Confusion of metaclasses."""


class Meta(type):
    def __new__(mcs, *args, **kwargs):
        print('Meta:')
        print(f'{__class__}.__new__()')
        return super().__new__(mcs, *args, **kwargs)


class SubMeta(Meta):
    def __new__(mcs, *args, **kwargs):
        print('SubMeta:')
        print(f'{__class__}.__new__()')

        # Skips over calling Meta.__new__()
        return super(Meta, mcs).__new__(mcs, *args, **kwargs)

        # Doesn't skip calling Meta.__new__()
        # return super().__new__(cls, *args, **kwargs)


class ConcreteMeta(metaclass=Meta):
    def __init__(self):
        print(f'{__class__}.__init__()')
        print(f'{self.__class__}')
        print(f'{self.__class__.__bases__}')
        print(f'type: {type(self.__class__)}')


class ConcreteSubMeta(metaclass=SubMeta):
    def __init__(self):
        print(f'{__class__}.__init__()')
        print(f'{self.__class__}')
        print(f'{self.__class__.__bases__}')
        print(f'type: {type(self.__class__)}')


if __name__ == '__main__':
    c1 = ConcreteMeta()
    c2 = ConcreteSubMeta()
