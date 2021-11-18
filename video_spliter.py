from genericpath import exists
import moviepy.editor
import os
from config import *
import shutil

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
                    text.replace('\u202a', '')
                    res_list.append((tuple(map(total_seconds, block.split(' --> '))), text))
    return res_list

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
                sub_video.write_videofile(f'content/video/{text}.mp4')
                sub_video.audio.write_audiofile(f'content/audio/{text}.mp3')
                if i > 3:
                    break

if __name__ == '__main__':

    file_list = list(filter(lambda x: os.path.isfile(path_to_dir+x), os.listdir(path_to_dir)))

    for file_name in file_list:
        split_video(file_name)

    # audio_list = list(filter(lambda x: x[-4:]=='.mp4', os.listdir('content/audio')))
