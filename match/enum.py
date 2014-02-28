class EnumBase(object):
  class Meta:
    allowed_types = tuple()
    zero_value = None

  @classmethod
  def names(klass, with_zero_value=True):
    def _get_names():
      names = []
      for n in dir(klass):
        if '__' not in n and n != 'Meta':
          value = getattr(klass, n)
          if isinstance(value, klass.Meta.allowed_types):
            if with_zero_value or value != klass.Meta.zero_value:
              names.append(n)
      return names

    if with_zero_value:
      if not hasattr(klass, '_cache__iterable_names_with_zero'):
        klass._cache__iterable_names_with_zero = _get_names()
      return klass._cache__iterable_names_with_zero
    else:
      if not hasattr(klass, '_cache__iterable_names_without_zero'):
        klass._cache__iterable_names_without_zero =  _get_names()
      return klass._cache__iterable_names_without_zero

  @classmethod
  def values(klass):
    return tuple(klass.iter())

  @classmethod
  def lookup(klass, instance):
    d = {}
    for n in klass.names():
      v = getattr(klass, n)
      if not isinstance(v, klass.Meta.allowed_types):
        continue
      d[v] = n
    return d[instance]

  @classmethod
  def reverse_lookup(klass, name):
    return dict(klass.choices(with_zero_value=True))[name]

  @classmethod
  def iter(klass):
    values = [getattr(klass, n) for n in klass.names()]
    values.sort()
    for v in values:
      if v == klass.Meta.zero_value:
        continue
      yield v

  @classmethod
  def next_value(cls, cur_value):
    index_of = cls.all().index(cur_value)
    return cls.all()[index_of + 1 % len(cls.all())]

  @classmethod
  def all(klass, with_zero_value=True):

    def _get_values():
      values = [getattr(klass, n) for n in klass.names(with_zero_value=with_zero_value) if isinstance(getattr(klass, n), klass.Meta.allowed_types)]
      values.sort()
      return values

    if with_zero_value:
      if not hasattr(klass, '_cache__iterable_values_with_zero'):
        klass._cache__iterable_values_with_zero = _get_values()
      return klass._cache__iterable_values_with_zero

    else:
      if not hasattr(klass, '_cache__iterable_values_without_zero'):
        klass._cache__iterable_values_without_zero = _get_values()
      return klass._cache__iterable_values_without_zero

  @classmethod
  def all_set(cls):
    if not hasattr(cls, "_cache__iterable_values_set"):
      cls._cache__iterable_values_set = set(cls.all())
    return cls._cache__iterable_values_set

  @classmethod
  def choices(klass, reverse=False, with_zero_value=False):
    lst = []
    for n in klass.names(with_zero_value=with_zero_value):
      v = getattr(klass, n)
      if reverse:
        lst.append((v, n))
      else:
        lst.append((n, v))
    return lst

class IntEnum(EnumBase):
  class Meta:
    allowed_types = (int, long,)
    zero_value = 0

class StringEnum(EnumBase):
  class Meta:
    allowed_types = (basestring,)
    zero_value = ''

class BooleanEnum(EnumBase):
  class Meta:
    allowed_types = (bool,)
    zero_value = None

class ListEnum(EnumBase):
  class Meta:
    allowed_types = (list, tuple,)
    zero_value = []

class FloatEnum(EnumBase):
  class Meta:
    allowed_types = (float,)
    zero_value = 0.0

"""
Some helper functions that makes using `enum` classes in python a little easier
"""

def generate_enum_reverse_lookup(klass):
  """
  Returns a lookup to verify that a certain value exists in an enum class
  And also returns to you it's Attribute Name in that class
  """
  dct = {}
  for k in dir(klass):
      if k.startswith('__'):
        continue

      val = getattr(klass, k, None)
      if not isinstance(val, (int, long)):
        continue

      if val in dct:
        raise ValueError('Can only have a value in a reverse lookup once, sorry dude')

      dct[val] = k

  return dct

def generate_choices_tuple(klass, reverse=False):
  lst = []
  for prop in dir(klass):
    if prop.startswith('_'):
      continue

    attr = getattr(klass, prop)
    if not isinstance(attr, (long,int)):
      continue

    if reverse:
      lst.append((attr, prop))
    else:
      lst.append((prop, attr))

  return tuple(lst)
