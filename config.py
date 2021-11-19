import genanki
import random
import data

def only_kana(X, min_value=4):
    allowed_chars = data.kana + data.simple_eng + data.simple_jp
    for x in X:
        if x not in allowed_chars:
            return False
    return len({x for x in data.kana} & {x for x in X}) >= min_value

def len_min(X, min_value=4):
  return len(X) >= min_value

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


ja_filter_funcs = [only_kana, len_min]
