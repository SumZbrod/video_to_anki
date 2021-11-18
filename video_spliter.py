from genericpath import exists
import moviepy.editor
import os
from config import *
import shutil
import genanki
import random
import pydub 
import numpy as np
import pydub 

def total_seconds(str_time: str) -> float:
    """
    Accept str about time ant calculate to float seconds
    """
    str_time = str_time.replace(',', '.')
    data = str_time.split(':')
    res = 0
    for i in range(3):
        res += 60**(2-i)*float(data[i])
    return res
    
def made_script_list(scr):
    """
    Accept subtitles 
    Return list of start and finish in seconds and text
    """
    res_list = []
    scr = scr.split('\n')
    for i, block in enumerate(scr):
        if '-->' in block and i<(len(scr)-1):
            if len(scr[1+i]) > 0:
                text = scr[1+i]
                if '\u202a' in text:
                    text = text[1:]
                    text = text.replace('\u202a', '')
                    res_list.append((tuple(map(total_seconds, block.split(' --> '))), text))
    return res_list

def write(f, x, sr=48000, normalized=False):
    """numpy array to MP3"""
    x = 30000*x
    channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
    if normalized:  # normalized array - each item should be a float in [-1, 1)
        y = np.int16(x * 2 ** 15)
    else:
        y = np.int16(x)
    song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
    song.export(f, format="mp3", bitrate="320k")

def split_video(file_name):
    file_path = path_to_dir+file_name
    file_name = file_name.split('.')[0]
    file_name = file_name.replace(' ', '_')
    script_path = f'scripts/{file_name}.srt'
    
    if os.path.exists(script_path) or os.system(f'ffmpeg -i {file_path} -map 0:s:0 {script_path}') == 0:
        with open(script_path) as f:
            script = f.read()
        script = made_script_list(script)
        with moviepy.editor.VideoFileClip(file_path) as video:
            for i, block in enumerate(script):
                delta_time, text = block
                sub_video = video.subclip(*delta_time)
                # sub_video.write_videofile(f'{video_path}{text}.mp4')
                write(f'{audio_path}{text}.mp3', sub_video.audio.to_soundarray())
                if i > 3:
                    break

def generate_deck(audio_list, deck_name):
    anki_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)
    for name in audio_list:
        print(name)
        note = genanki.Note(model=anki_model, fields=[f'[sound:{name}]', name.split('.')[0]])
        anki_deck.add_note(note)
    my_package = genanki.Package(anki_deck)
    my_package.media_files = list(map(lambda x: audio_path+x, audio_list))
    my_package.write_to_file(f'{deck_name}.apkg')
    # .write_to_file(f'{deck_name}.apkg')
    # genanki.Package(my_package).write_to_file(f'{deck_name}.apkg')

if __name__ == '__main__':

    file_list = list(filter(lambda x: os.path.isfile(path_to_dir+x), os.listdir(path_to_dir)))

    for file_name in file_list:
        break
        split_video(file_name)

    audio_list = list(filter(lambda x: x[-4:]=='.mp3', os.listdir(audio_path)))
    # audio_list = list(filter(lambda x: x[-4:]=='.mp3', os.listdir()))
    # video_list = list(filter(lambda x: x[-4:]=='.mp4', os.listdir(audio_path)))

    generate_deck(audio_list, 'test_')
    
