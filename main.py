import os
import requests
import numpy as np
import time
import subprocess
import json
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
import re

np.seterr(over='ignore')
key_api = "AIzaSyAdO-hmFHLaRgiARrMRNdpN9RqgYx_ulB4"

pwd = os.getcwd()
pwd = pwd + '/'


def check_exist_chapt(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")

    lines = fo.readlines()
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '').split(',')

            if (str(series_current) == str(id_series)):
                if str(id_chapt_new) in list_chapt_current:
                    return False
    fo.close()
    return True


def save_to_file(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")
    lines = fo.readlines()
    check = True
    i = 0
    len_lines = len(lines)
    n = '\n'
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '')

            if (i == len_lines - 1):
                n = ''
            if (str(series_current) == str(id_series)):
                list_chapt_current = str(id_series) + ':' + str(list_chapt_current) + ',' + str(id_chapt_new) + n
                lines[i] = list_chapt_current
                check = False
        i = i + 1
    if (check):
        if (len(lines) > 0):
            lines[len(lines) - 1] = lines[len(lines) - 1] + '\n'
        lines.append(str(id_series) + ':' + id_chapt_new)
    fo.close()

    fo = open(name_file, "w")
    fo.writelines(lines)
    fo.close()
    return True


def upload_youtube_and_check_out_number(title, description, tags, file_name, playlist, stt_id):
    stdout = subprocess.check_output(['youtube-upload', '--title=' + str(title) + '', '--tags="' + str(tags) + '"',
                                '--description=' + str(description) + '', '--playlist=' + str(playlist),
                                      '--client-secrets=client_secrets.json',
                                '--credentials-file=' + str(stt_id) + '/credentials.json', str(file_name)])

    print(stdout)
    return len(str(stdout)) > 0



def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if(len(lines) == 0):
        return True

    return False


def get_file_upload(stt_id):
    filelist = os.listdir(str(stt_id) + '/input')

    for fichier in filelist:
        if "input.mp4" in fichier:
            return fichier

    return False


def get_ffmpeg(file_video, file_ffmpeg, stt_id):
    path_file = 'ffmpeg-files/' + file_ffmpeg
    fo = open(path_file, "r")
    lines = fo.readlines()

    if len(lines) > 0:
        string_process = lines[0]
        string_process = string_process.replace("input.mp4", str(stt_id) + '/input/input.ts')
        string_process = string_process.replace("output.mp4", str(stt_id) + "/output/" + str(file_video))

        return string_process

    return False


def process_video(file_name, length_cut, stt_id):
    total_lentgh = getLength(stt_id)

    string1 = "ffmpeg -ss " + str(length_cut) + " -i " + str(stt_id) + "/input/input.mp4 -t " \
              + str(total_lentgh) + " -c copy " + str(stt_id) + "/input/temp_input.mp4"
    os.system(string1)

    string = "ffmpeg -i " + str(stt_id) + "/input/temp_input.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts " + str(stt_id) + "/input/input.ts"
    os.system(string)

    string_ffmpeg = get_ffmpeg(file_name, 'text3.txt', stt_id)
    os.system(string_ffmpeg)

    return str(stt_id) + '/output/' + str(file_name)


def get_data_file(stt_id, file_name):
    path_file = str(stt_id) + '/' + file_name + '.txt'
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) > 0:
        stt_video = lines[0]

    return stt_video


def update_stt_video(stt_id, stt_video):
    path_file = str(stt_id) + '/stt-video.txt'
    fo = open(path_file, "w")
    fo.write(str(stt_video))
    fo.close()


def getLength(stt_id):
    filename = str(stt_id) + "/input/input.mp4"
    clip = VideoFileClip(filename)

    return clip.duration


def hanlde(name_title, description, genres, stt_id, length_cut):
    check = False

    file_name = get_file_upload(stt_id)

    file_name = process_video(file_name, length_cut, stt_id)

    playlist = ''
    print(name_title)

    if file_name:
        print("Uploading...")
        #isFirstUpload(stt_id)
        if True:
            os.system('youtube-upload --title="' + str(
                name_title) + '" --description="' + description + '" --tags="' + genres +
                      '" --playlist="' + str(playlist) + '" --client-secrets="client_secrets.json" --credentials-file="'
                      + str(stt_id) + '/credentials.json" ' + str(file_name))

            check = True
        else:
            check = upload_youtube_and_check_out_number(name_title, description, genres, file_name, playlist, stt_id)

    os.remove(str(stt_id) + '/input/input.mp4')
    os.remove(str(stt_id) + '/input/temp_input.mp4')
    os.remove(str(stt_id) + '/input/input.ts')
    os.remove(str(stt_id) + '/output/input.mp4')

    return check


def download_video_from_youtube(id_video, stt_id):
    number = get_number_video("https://www.youtube.com/watch?v=" + str(id_video))

    if number == False:
        return False

    print("Downloading...")
    url = "youtube-dl -f " + str(number) + " -o '" + str(stt_id) + "/input/input.%(ext)s' https://www.youtube.com/watch?v=" + str(id_video)
    print(url)
    os.system(url)

    return True


def get_tags(id_video):
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=" + key_api + "&id=" + str(id_video)

    req = requests.get(url)
    items = json.loads(req.content)
    tags = ''

    try:
        tags = items['items'][0]['snippet']['tags']
    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))

    list_tag = ','.join(tags)

    return list_tag


def update_max_video(stt_id):
    stt_video = get_data_file(stt_id, 'max-video')
    stt_video = int(stt_video) - 1

    path_file = str(stt_id) + '/max-video.txt'
    fo = open(path_file, "w")
    fo.write(str(stt_video))
    fo.close()


def get_list_video(channel_id, length_cut, stt_id):
    print("Get list video..")
    max_result = 5

    url = "https://www.youtube.com/channel/" + str(channel_id) + "/videos"

    req = requests.get(url)
    content = BeautifulSoup(req.content, "lxml")
    items = content.find_all(class_="yt-lockup-content")
    stt = 1

    for item in items:
        if stt > max_result:
            break
        a = item.find("a")
        title = a.get('title') + ' - LOL Highlight'
        title = remove_special_characters(title)
        description = title

        id_video = a.get('href').replace("/watch?v=", "")

        if check_exist_chapt(channel_id, id_video, stt_id):
            tags = get_tags(id_video)
            tags = ''

            check = False
            has_video = download_video_from_youtube(id_video, stt_id)

            if has_video:
                check = hanlde(title, description, tags, stt_id, length_cut)
            else:
                save_to_file(channel_id, id_video, stt_id)

            if check:
                save_to_file(channel_id, id_video, stt_id)

                print("Done")
                time.sleep(150)

        stt = stt + 1


def get_source_links(stt_id):
    # read file get arr website avail
    fo = open(stt_id + "/source-links.txt", "r")
    arr_website_avail = []
    lines = fo.readlines()

    for line in lines:
        arr_website_avail.append(line.replace('\n', ''))
    fo.close()
    return arr_website_avail


def remove_special_characters(string):
    # string = string.replace('\r', '')
    # string = string.replace(' : ', '-')
    # string = string.replace(' ', '-')
    # string = string.replace('.', '-')
    #
    # return re.sub(r'[^a-zA-Z0-9-\n\.]', '', string)
    string = string.replace('\r', '')
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('|', '')
    string = string.replace('-', '')

    return string


def get_number_video(url):
    try:
        stdout = subprocess.check_output(['youtube-dl', '-F', url])
        arr = str(stdout).split('\\n')

        audio = ''

        for item in arr:
            if 'm4a' in item:
                audio = item.split(' ')[0]

        for item in arr:
            if '720p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '480p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '360p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '240p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)
    except:
        return False

    return True


if __name__ == '__main__':
    stt_id = str(input("Enter id: "))
    arr_website_avail = get_source_links(stt_id)

    for item in arr_website_avail:
        arr_item = item.split(",")
        item_web = arr_item[0]
        length_cut = arr_item[1]

        get_list_video(item_web, length_cut, stt_id)

