import genanki
# from numpy import random
# import numpy as np
import random
# raw videos
path_to_dir = 'videos/'

# clips
audio_path = 'content/audio/'
video_path = 'content/video/'

# deck

anki_model = genanki.Model(
  random.randrange(1 << 30, 1 << 31),
  'A model for training listening',
  fields=[
    {'name': 'Audio_question'},
    {'name': 'Video_answer'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Audio_question}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Video_answer}}',
    },
  ])