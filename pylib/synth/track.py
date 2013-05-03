import wave
import struct

from synth.channel import SampledChannel

gFmt = {
  1: 'b',
  2: 'h',
  4: 'i',
  8: 'q',
}

def chunks(s, n):
  for i in xrange(0, len(s), n):
    yield s[i:i+n]

def format_info(width):
  if width not in gFmt:
    raise ValueError("Unsupported sample width: {}".format(width))
  return gFmt[width], (1 << (8 * width - 1)) - 1

class Track(object):

  def __init__(self, *args):
    self.channels = list(args)

  @classmethod
  def read(self, path):
    fp = wave.open(path, "r")
    channels = fp.getnchannels()
    width = fp.getsampwidth()
    frequency = fp.getframerate()
    length = fp.getnframes() / float(frequency)
    track = Track(
      *(SampledChannel(length, frequency=frequency) for i in range(channels))
    )

    fmt_char, max_value = format_info(width)
    fmt = "<" + fmt_char * channels
    
    frames = fp.readframes(2048)
    i = 0
    
    while frames:
      for chunk in chunks(frames, channels*width):
        sample = struct.unpack(fmt, chunk)
        for (c, channel_value) in enumerate(sample):
          value = channel_value / float(max_value)
          track.channels[c].data[i] = value
        i += 1
      frames = fp.readframes(2048)

    return track

  @property
  def nchannels(self):
    return len(self.channels)

  @property
  def length(self):
    return max(*(x.length for x in self.channels))

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
      data += struct.pack(fmt, *sample)

    fp.writeframes(data)
    fp.close()

  def samples(self, length, frequency):
    frames = int(length * frequency)
    for i in range(frames):
      t = float(i) / frequency
      yield self.eval(t)

  def eval(self, t):
    return tuple(f.eval(t) for f in self.channels)
