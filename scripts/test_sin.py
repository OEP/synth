#!/usr/bin/env python
from synth.track import Track
from synth.trig import Sin
from synth.channel import *

def main():
  s = Sin()
  f = Transform(s, frequency=1000)
  g = Transform(s, frequency=0.5)

  fog = f(g)
  
  ## Mono test
  t = Track(fog)
  t.write('sin-mono.wav', 1.0)

  ## Stereo test
  t = Track(fog,f)
  t.write('sin-stereo.wav', 1.0)

if __name__ == "__main__":
  main()
