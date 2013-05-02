import numpy as np

def Coerce(self, x):
  if isinstance(x, Channel): return x
  if isinstance(x, (int, float)): return Constant(x)
  raise ValueError("Could not be coerced: {}".format(x))

class Channel(object):
  def __init__(self):
    pass

  def __call__(self, t):
    raise NotImplementedError("Subclass must implement __call__")

  def __add__(self, other):
    return Sum(self, Coerce(other))

  def __sub__(self, other):
    return Difference(self, Coerce(other))

  def __mul__(self, other):
    return Product(self, Coerce(other))

  def __div__(self, other):
    return Quotient(self, Coerce(other))

class Constant(Channel):
  def __init__(self, c):
    self.c = c

  def __call__(self, t):
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

  def __call__(self, t):
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
    self.a = a
    self.b = b

class Sum(BinaryOp):
  def __call__(self, t):
    return self.a(t) + self.b(t)

class Difference(BinaryOp):
  def __call__(self, t):
    return self.a(t) - self.b(t)

class Product(BinaryOp):
  def __call__(self, t):
    return self.a(t) * self.b(t)

class Quotient(BinaryOp):
  def __call__(self, t):
    return self.a(t) / self.b(t)
