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
    {'name': 'kanji'}
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Audio_question}}',              # AND THIS
      # 'afmt': '{{FrontSide}}<hr id="answer">{{Video_answer}}',
      'afmt': '{{FrontSide}}<hr id="answer"><span style="font-family: Liberation Sans; font-size: 40px;  ">{{kanji}}<br>{{Video_answer}}</span>'
    }],
  css="""
  .card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}

.card1 { background-color: #ffffff; }
.card2 { background-color: #ffffff; }
.card3 { background-color: #ffffff; }
  """
  )
