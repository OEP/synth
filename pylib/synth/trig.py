import math
from synth.channel import Channel

class Sin(Channel):
  def eval(self, t):
    return math.sin(2 * math.pi * t)

class Cos(Channel):
  def eval(self, t):
    return math.cos(2 * math.pi * t)

class Tan(Channel):
  def eval(self, t):
    return math.tan(2 * math.pi * t)

class Sawtooth(Channel):
  def eval(self, t):
    return -1 + 2 * (t - math.floor(t))

class Square(Channel):
  def __init__(self, duty=0.5, *args, **kwargs):
    self.duty = duty

  def eval(self, t):
    return 1.0 if (t - math.floor(t)) < self.duty else -1.0
