import numpy as np
import math

class Channel(object):
  def __init__(self):
    pass

  def eval(self, t):
    raise NotImplementedError("Subclass must implement eval")
  
  @property
  def name(self):
    return self.__class__.__name__

  @property
  def derivative(self):
    raise NotImplementedError("%s has not implemented derivative" % self.name)

  def reduce(self):
    return self

  def __call__(self, t):
    return self.eval(t)

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

  def __neg__(self):
    return Invert(self)

  def __abs__(self):
    return Abs(self)

  def __pow__(self, other):
    return Power(self, other)

  def __rpow__(self, other):
    return Power(other, self)

  def __coerce__(self, other):
    if isinstance(other, Channel): return (self, other)
    if isinstance(other, (int, float)): return (self, Constant(other))
    return NotImplemented

class Identity(Channel):
  def eval(self, t):
    return t

  @property
  def derivative(self):
    return Constant(0)

  def __repr__(self):
    return "t"
  
class SampledChannel(Channel):
  def __init__(self, length, frequency=48000):
    super(SampledChannel, self).__init__()
    frames = math.ceil(float(length) * frequency)
    self.length = length
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

class Constant(Channel):
  def __init__(self, c):
    self.c = c

  def eval(self, t):
    return self.c

  @property
  def derivative(self):
    return Constant(0)

  def __repr__(self):
    return str(self.c)

class UnaryOp(Channel):
  def __init__(self, a, *args, **kwargs):
    super(UnaryOp, self).__init__(*args, **kwargs)
    if isinstance(a, (float, int)):
      a = Constant(a)
    self.a = a
  
  def reduce(self):
    ra = self.a.reduce()
    cls = self.__class__
    if isinstance(ra, Constant):
      tmp = cls(ra)
      return Constant(tmp.eval(0.0))
    return super(Invert, self).reduce()

  def __repr__(self):
    return "{}({})".format(self.name, self.a)

class Invert(UnaryOp):
  def eval(self, t):
    return -self.a(t)

  @property
  def derivative(self):
    return -self.a.derivative

class Abs(UnaryOp):
  def eval(self, t):
    return abs(self.a(t))

  @property
  def derivative(self):
    return self.a * self.a.derivative / ((self.a ** 2) ** 0.5)

class Log(UnaryOp):
  def eval(self, t):
    return math.log(self.a.eval(t))

class BinaryOp(Channel):
  def __init__(self, a, b):
    super(BinaryOp, self).__init__()
    a, b = coerce(a,b)
    self.a = a
    self.b = b
  
  def reduce(self):
    ra = self.a.reduce()
    rb = self.b.reduce()
    cls = self.__class__
    if isinstance(ra, Constant) and isinstance(rb, Constant):
      tmp = cls(ra, rb)
      return Constant(self.eval(0.0))
    return super(Invert, self).reduce()
  
  def __repr__(self):
    return "{}({}, {})".format(self.name, repr(self.a), repr(self.b))

class Power(BinaryOp):
  def eval(self, t):
    return self.a.eval(t) ** self.b.eval(t)

  # f(x)^(g(x)-1)     (g(x) f'(x) + f(x) log(f(x)) g'(x))
  @property
  def derivative(self):
    return (self.a ** (self.b - 1)) * \
      (self.b * self.a.derivative + self.a * Log(self.a) * self.b.derivative)
    
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


