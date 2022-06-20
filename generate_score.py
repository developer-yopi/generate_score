import requests
from bs4 import BeautifulSoup
from lxml import etree
import subprocess
import os
from zipfile import ZipFile
import csv


def main():
    # コード情報の取得
    res = requests.get("https://gakufu.gakki.me/m/data/M00040.html")
    soup = BeautifulSoup(res.text, 'html.parser')
    tag_obj = soup.find_all('span', class_='cd_fontpos')
    text = [x.text for x in tag_obj]
    # chord.txtに出力
    with open('chord.txt', 'w') as f:
        print(text, file=f)

    # ファイル名のリストを取得
    file_list = os.listdir()
    for file in file_list:
        if file.endswith('.mscz'):
            mscz = file
            break

    title = mscz.replace('.mscz', '')
    tmp_dir = './tmp/'
    # subprocess.run(['mkdir', '-p', tmp_dir])
    subprocess.run(['mkdir', tmp_dir])

    # msczをunzipし、mscxをtmpディレクトリに格納
    with ZipFile(mscz, 'r') as mscx_zip:
        file_names = mscx_zip.namelist()
        print(file_names)
        for file_name in file_names:
            mscx_zip.extract(file_name, tmp_dir)
            if file_name.endswith('.mscx'):
                mscx_zip.extract(file_name, tmp_dir)
                mscx = tmp_dir + title + '.mscx'
                subprocess.run(['mv', tmp_dir + file_name, mscx])
                # break

    # mscxをparse
    tree = etree.parse(mscx)
    root = tree.getroot()   

    staffs = tree.xpath('//Staff')
    for i, staff in enumerate(staffs[len(staffs)//2:]):
        for voice in staff.xpath('./Measure/voice'):
            for rest in voice.xpath('./Rest'):
                if i == 0:  # 一番上の段にのみコード情報を入れる
                    root, name, base = separate_chord()
                    voice.append(new_harmony(root=root, name=name, base=base))
                # 休符を消し音符を入力
                voice.remove(rest)
                voice.append(new_chord())

    # print(etree.tostring(tree).decode())

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
def new_chord():
    # chord要素の準備
    chord_elem = etree.Element('Chord')
    duration_type_elem = etree.Element('durationType')
    note_elem = etree.Element('Note')
    pitch_elem = etree.Element('pitch')
    tpc_elem = etree.Element('tpc')

    # 要素に内容を書き込む
    duration_type_elem.text = 'whole'   # 全音符
    pitch_elem.text = '60'              # C4
    tpc_elem.text = '14'                # C

    # 親子関係の構築
    chord_elem.append(duration_type_elem)
    chord_elem.append(note_elem)
    note_elem.append(pitch_elem)
    note_elem.append(tpc_elem)

    return chord_elem

# 新しいharmony要素
def new_harmony(root:int=14, name:str=None, base:int=None):
    # harmony要素の準備
    harmony_elem = etree.Element('Harmony')
    root_elem = etree.Element('root')
    root_case_elem = etree.Element('rootCase')
    name_elem = etree.Element('name')
    base_elem = etree.Element('base')
    base_case_elem = etree.Element('baseCase')

    # 要素に内容を書き込む
    root_elem.text = str(root)
    root_case_elem.text = '1'
    name_elem.text = name
    base_elem.text = str(base)
    base_case_elem.text = '1'

    # 親子関係の構築
    harmony_elem.append(root_elem)
    harmony_elem.append(root_case_elem)
    if name:  # コード名が存在する場合
        harmony_elem.append(name_elem)
    if base != None:  # 基音が根音と異なる場合
        harmony_elem.append(base_elem)
        harmony_elem.append(base_case_elem)
    return harmony_elem

# 音名から Tonal Pitch Class を取得する
def get_tpc(note: str='C'):
    return 14

# コードのテキストを root, name, base に分ける
def separate_chord(chord: str='Cmaj7'):
    # 根音はコード名の先頭の文字
    root = get_tpc(note=chord[0])
    # 分数コードはコード名と基音を分ける
    if '/' in chord:
        name = chord[1:-1]
        base = get_tpc(chord[-1])
    elif 'on' in chord:
        name = chord[1:-2]
        base = get_tpc(chord[-1])
    # 分数コードでない場合、基音は None
    else:
        name = chord[1:]
        base = None
    return root, name, base


if __name__ == "__main__":
    main()