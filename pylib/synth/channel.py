import numpy as np

class Channel(object):
  def __init__(self):
    pass

  def eval(self, t):
    raise NotImplementedError("Subclass must implement eval")

  def __add__(self, other):
    return Sum(self, other)

  def __sub__(self, other):
    return Difference(self, other)

  def __mul__(self, other):
    return Product(self, other)

  def __div__(self, other):
    return Quotient(self, other)

  def __coerce__(self, other):
    if isinstance(other, Channel): return (self, other)
    if isinstance(other, (int, float)): return (self, Constant(other))
  
class Constant(Channel):
  def __init__(self, c):
    self.c = c

  def eval(self, t):
    return self.c

class SampledChannel(Channel):
  def __init__(self, length, frequency=48000):
    super(SampledChannel, self).__init__()
    frames = int(float(length) * frequency)
    self.frequency = frequency
    self.data = np.zeros(frames)

  @property
  def frames(self):
    return len(self.data)

  def __getitem__(self, i):
    if i < 0 or i >= self.frames: return 0.0
    return self.data[i]

  def eval(self, t):
    ndx = float(t) * self.frequency
    i = int(ndx)
    q = ndx - i
    return self[i] * (1-q) + self[i+1] * q

  def sample(self, f):
    for i in range(self.frames):
      t = float(i) / self.frequency
      self.data[i] = f(t)

class BinaryOp(Channel):
  def __init__(self, a, b):
    super(BinaryOp, self).__init__()
    a, b = coerce(a,b)
    self.a = a
    self.b = b

class Sum(BinaryOp):
  def eval(self, t):
    return self.a(t) + self.b(t)

class Difference(BinaryOp):
  def eval(self, t):
    return self.a(t) - self.b(t)

class Product(BinaryOp):
  def eval(self, t):
    return self.a(t) * self.b(t)

class Quotient(BinaryOp):
  def eval(self, t):
    return self.a(t) / self.b(t)

class Transformable(Channel):
  def __init__(self, shift=0.0, amplitude=1.0, frequency=1.0, *args, **kwargs):
    super(Transformable, self).__init__(*args, **kwargs)
    self.shift = shift
    self.amplitude = amplitude
    self.frequency = frequency

class Transform(Transformable):
  def __init__(self, f, *args, **kwargs):
    super(Transform, self).__init__(*args, **kwargs)
    self.f = f

  def eval(self, t):
    return self.amplitude * self.f(self.frequency * t - self.shift)


