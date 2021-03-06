import moviepy.editor
import os
from config import *
import genanki
import random
from moviepy.video.tools.subtitles import SubtitlesClip
from time import time
import numpy as np
import re

def total_seconds(str_time: str) -> float:
    """
    Accept str about time ant calculate to float seconds
    """
    # print(str_time)
    str_time = str_time.replace(',', '.')
    data = str_time.split(':')
    res = 0
    for i in range(3):
        res += 60**(2-i)*float(data[i])
    return res
    
def made_script_list(script, filter_funcs=None):
    """
    Accept subtitles 
    Return list of start and finish in seconds and text
    """
    if filter_funcs == None:
        filter_funcs = [lambda x: True]
    re_bracket = list(set(re.findall(r'(（.+?）)', script))) + ['\u202a', '{\\an8}', '\u3000']
    for r in re_bracket:
        script = script.replace(r, '')
    res_list = []
    for scr in script.split('\n\n'):
        scr = scr.split('\n')
        text = '\n'.join(scr[2:])
        allowed_flag = True
        for b_func in filter_funcs:
            allowed_flag &= b_func(text) 
        if allowed_flag:
            res_list.append((tuple(map(total_seconds, scr[1].split(' --> '))), text))
    return res_list

def split_video(file_name):
    file_path = path_to_dir+file_name
    file_name = file_name.split('.')[0]
    file_name = file_name.replace(' ', '_')
    script_path = f'scripts/{file_name}.srt'
    # generator = lambda txt: moviepy.editor.TextClip(txt, font='Arial', fontsize=16, color='white')

    if os.path.exists(script_path) or os.system(f'ffmpeg -i {file_path} -map 0:s:0 {script_path}') == 0:
        with open(script_path) as f:
            script = f.read()
        script = made_script_list(script, ja_filter_funcs)
        with moviepy.editor.VideoFileClip(file_path) as video:
            i = 0
            np.random.shuffle(script)
            for block in script:
                # if i == 10:
                    # break
                delta_time, text = block        
                title = f'{file_name}#{text}'
                if os.path.exists(title+'.mp3') and os.path.exists(title+'.mp4'):
                    continue
                sub_video = video.subclip(*delta_time)
                sub_video.audio.write_audiofile(f'{audio_path}{file_name}#{text}.mp3')
                # subs = [(tuple(map(round, delta_time)), text)]
                # print(subs)
                # subtitles = SubtitlesClip(subs, generator)
                # sub_video = moviepy.editor.CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])
                sub_video.write_videofile(f'{video_path}{file_name}#{text}.mp4')
                # write(f'{audio_path}{text}.mp3', sub_video.audio.to_soundarray())
                i += 1

def generate_deck(audio_list, deck_name):
    anki_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)
    for name in audio_list:
        # note = genanki.Note(model=anki_model, fields=[f'[sound:{name}]', name.split('.')[0]])
        note = genanki.Note(model=anki_model, fields=[f'[sound:{name}]', f'[sound:{name[:-1]}4]', name.split('#')[1][:-4]])
        anki_deck.add_note(note)
    my_package = genanki.Package(anki_deck)
    my_package.media_files = list(map(lambda x: audio_path+x, audio_list)) + list(map(lambda x: video_path+x[:-1]+'4', audio_list))
    my_package.write_to_file(f'{deck_name}.apkg')
    # .write_to_file(f'{deck_name}.apkg')
    # genanki.Package(my_package).write_to_file(f'{deck_name}.apkg')


if __name__ == '__main__':
    start = time()
    min_length = 4
    file_list = list(filter(lambda x: os.path.isfile(path_to_dir+x), os.listdir(path_to_dir)))

    for file_name in file_list:
        split_video(file_name)

    audio_list = list(filter(lambda x: x[-4:]=='.mp3', os.listdir(audio_path)))

    generate_deck(audio_list, 'komisan')
    
    print(f'{time()-start} seconds for {len(audio_list)} cards')
