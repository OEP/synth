import wave
import struct

gFmt = {
  1: 'b',
  2: 'h',
  4: 'i',
  8: 'q',
}

def format_info(width):
  if width not in gFmt:
    raise ValueError("Unsupported sample width: {}".format(width))
  return gFmt[width], (1 << (8 * width - 1)) - 1

class Track(object):

  def __init__(self, *args):
    self.channels = list(args)

  @property
  def nchannels(self):
    return len(self.channels)

  def write(self, path, length, frequency=48000, width=2):
    fp = wave.open(path, "w")
    fp.setnchannels(self.nchannels)
    fp.setsampwidth(width)
    fp.setframerate(frequency)
    fp.setnframes(int(length * frequency))

    fmt_char, max_value = format_info(width)
    data = bytes()
    fmt = "<" + fmt_char * self.nchannels
    for sample in self.samples(length, frequency):
      sample = tuple(int(max_value * x) for x in sample)
      data += struct.pack("<" + fmt_char * self.nchannels, *sample)

    fp.writeframes(data)
    fp.close()

  def samples(self, length, frequency):
    frames = int(length * frequency)
    for i in range(frames):
      t = float(i) / frequency
      yield self.eval(t)

  def eval(self, t):
    return tuple(f(t) for f in self.channels)
