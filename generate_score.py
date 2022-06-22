import subprocess
import os
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd

import scoremodule as sm


def main(url: str="https://gakufu.gakki.me/m/index2.php?p=RQ10738&k=m1#rp"):
    # コード情報の取得
    # url = "https://gakufu.gakki.me/m/data/M00040.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    tag_obj = soup.find_all('span', class_='cd_fontpos')
    chord_list = [
        chord.text
        .replace('â\x99\xad', 'b')  # ♭ を b に置き換える
        .replace('ï¼\x83', '#')     # ＃ を # に置き換える
        .replace('on', '/')         # on を / に置き換える
        for chord in tag_obj
    ]
    # chord.txtに出力
    with open('chord.txt', 'w') as f:
        chords = [chord + '\n' for chord in chord_list]
        f.writelines(chords)

    # ファイル名を取得
    file_list = os.listdir()
    for file in file_list:
        if file.endswith('.mscz'):
            mscz = file
            break
    
    title = mscz.replace('.mscz', '')
    tmp_dir = './tmp/'
    subprocess.run(['mkdir', tmp_dir])

    # msczをunzipし、mscxをtmpディレクトリに格納
    with ZipFile(mscz, 'r') as mscx_zip:
        file_names = mscx_zip.namelist()
        for file_name in file_names:
            mscx_zip.extract(file_name, tmp_dir)
            if file_name.endswith('.mscx'):
                mscx_zip.extract(file_name, tmp_dir)
                mscx = tmp_dir + title + '.mscx'
                subprocess.run(['mv', tmp_dir + file_name, mscx])

    tree = etree.parse(mscx)
    staffs = tree.xpath('//Staff')
    for i, staff in enumerate(staffs[len(staffs)//2:]):  # パート
        for j, voice in enumerate(staff.xpath('./Measure/voice')):  # 小節
            chord = chord_list[j]
            root, name, base = sm.separate_chord(chord)
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                if i == 0:  # 一番上の段にのみコード情報を入れる
                    voice.insert(k, sm.new_harmony(root=root, name=name, base=base))
                elif i == 4:  # Bassを入力
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    if base:
                        voice.append(sm.new_chord(pitch=sm.tpc_to_pitch(base, 42), tpc=base))
                    else:
                        voice.append(sm.new_chord(pitch=sm.tpc_to_pitch(root, 42), tpc=root))

    # ファイル出力
    tree.write(
        # mscx,
        './a.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )


if __name__ == "__main__":
    main()