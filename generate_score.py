import subprocess
import os
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd


def main(url: str="https://gakufu.gakki.me/m/index2.php?p=RQ10738&k=m1#rp"):
    # コード情報の取得
    # url = "https://gakufu.gakki.me/m/data/M00040.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    tag_obj = soup.find_all('span', class_='cd_fontpos')
    chord_list = [x.text.replace('â\x99\xad', 'b').replace('ï¼\x83', '#').replace('on', '/') for x in tag_obj]
    # chord.txtに出力
    with open('chord.txt', 'w') as f:
        print(chord_list, file=f)

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
            root, name, base = separate_chord(chord)
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                if i == 0:  # 一番上の段にのみコード情報を入れる
                    voice.insert(k, new_harmony(root=root, name=name, base=base))
                elif i == 4:  # Bassを入力
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    voice.append(new_chord(pitch=42, tpc=root))

    # ファイル出力
    tree.write(
        # mscx,
        './a.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )


### 関数 ###

# 新しいchord要素
def new_chord(pitch: int, tpc: int):
    # chord要素の準備
    chord_elem = etree.Element('Chord')
    duration_type_elem = etree.Element('durationType')
    note_elem = etree.Element('Note')
    pitch_elem = etree.Element('pitch')
    tpc_elem = etree.Element('tpc')

    # 要素に内容を書き込む
    duration_type_elem.text = 'whole'   # 全音符
    pitch_elem.text = str(pitch)
    tpc_elem.text = str(tpc)

    # 親子関係の構築
    chord_elem.append(duration_type_elem)
    chord_elem.append(note_elem)
    note_elem.append(pitch_elem)
    note_elem.append(tpc_elem)

    return chord_elem

# 新しいharmony要素
def new_harmony(root: int, name: str, base: int):
    # harmony要素の準備
    harmony_elem = etree.Element('Harmony')
    root_elem = etree.Element('root')
    name_elem = etree.Element('name')
    base_elem = etree.Element('base')

    # 要素に内容を書き込む
    root_elem.text = str(root)
    name_elem.text = name
    base_elem.text = str(base)

    # 親子関係の構築
    harmony_elem.append(root_elem)
    if name:  # コード名が存在する場合
        harmony_elem.append(name_elem)
    if base != None:  # 基音が根音と異なる場合
        harmony_elem.append(base_elem)
    return harmony_elem

# 音名から Tonal Pitch Class を取得する
def tpc(note: str) -> int:
    df = pd.read_csv('csv/tpc.csv', index_col='tpc')
    tpc = int(df[df['pitch'] == note].index[0])
    return tpc

# コードを根音、コード名、基音に分ける
def separate_chord(chord: str):
    # 根音はコード名の先頭の文字
    root_name = chord[0]
    if len(chord) > 1:
        if chord[1] == '#' or chord[1] == 'b':
            root_name = chord[:2]
    root = tpc(root_name)

    # 分数コードはコード名と基音を分ける
    if '/' in chord:
        if chord[-1] == '#' or chord[-1] == 'b':
            name = chord[len(root_name):-3]
            base = tpc(chord[-2:])
        else:
            name = chord[len(root_name):-2]
            base = tpc(chord[-1])

    # 分数コードでない場合、基音は None
    else:
        name = chord[len(root_name):]
        base = None

    return root, name, base


if __name__ == "__main__":
    main()