#!/usr/bin/env python
from synth.track import Track
from synth.trig import Sin
from synth.channel import *

def main():
  s = Sin()
  f = Transform(s, frequency=1000)
  g = Transform(s, frequency=800)
  
  ## Mono test
  t = Track(f)
  t.write('sin-mono.wav', 1.0)

  ## Stereo test
  t = Track(f,g)
  t.write('sin-stereo.wave', 1.0)


if __name__ == "__main__":
  main()
