import numpy as np

class Channel(object):
  def __init__(self):
    pass

  def eval(self, t):
    raise NotImplementedError("Subclass must implement eval")

  def __call__(self, other):
    return PassThrough(self, other)

  def __add__(self, other):
    return Sum(self, other)

  def __radd__(self, other):
    return self + other

  def __sub__(self, other):
    return Difference(self, other)

  def __rsub__(self, other):
    a, b = coerce(self, other)
    return b - a

  def __mul__(self, other):
    return Product(self, other)

  def __rmul__(self, other):
    return self * other

  def __div__(self, other):
    return Quotient(self, other)

  def __rdiv__(self, other):
    a, b = coerce(self, other)
    return b / a

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
      self.data[i] = f.eval(t)

class UnaryOp(Channel):
  def __init__(self, a, *args, **kwargs):
    super(UnaryOp, self).__init__(*args, **kwargs)
    if isinstance(a, (float, int)):
      a = Constant(a)
    self.a = a

class Invert(UnaryOp):
  def eval(self, t):
    return -self.a(t)

class BinaryOp(Channel):
  def __init__(self, a, b):
    super(BinaryOp, self).__init__()
    a, b = coerce(a,b)
    self.a = a
    self.b = b

class PassThrough(BinaryOp):
  def eval(self, t):
    return self.a.eval(self.b.eval(t))

class Sum(BinaryOp):
  def eval(self, t):
    return self.a.eval(t) + self.b.eval(t)

class Difference(BinaryOp):
  def eval(self, t):
    return self.a.eval(t) - self.b.eval(t)

class Product(BinaryOp):
  def eval(self, t):
    return self.a.eval(t) * self.b.eval(t)

class Quotient(BinaryOp):
  def eval(self, t):
    return self.a.eval(t) / self.b.eval(t)

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
    return self.amplitude * self.f.eval(self.frequency * t - self.shift)


