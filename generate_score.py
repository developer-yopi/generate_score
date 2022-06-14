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
    for x in file_list:
        if x.endswith('.mscz'):
            mscz = x
            break

    title = mscz.replace('.mscz', '')
    tmp = title + '/tmp'
    subprocess.run(['mkdir', '-p', tmp])

    # msczをunzipし、mscxをtmpディレクトリに格納
    with ZipFile(mscz, 'r') as mscx_zip:
        file_names = mscx_zip.namelist()
        for file_name in file_names:
            if file_name.endswith('.mscx'):
                mscx_zip.extract(file_name, tmp)
                break
    # mscx = tmp + '/' + title + '.mscx'

    # mscxをparse
    tree = etree.parse(tmp + '/' + title + '.mscx')
    root = tree.getroot()   

    staffs = tree.xpath('//Staff')
    for staff in staffs[len(staffs)//2:]:
        for voice in staff.xpath('./Measure/voice'):
            for rest in voice.xpath('./Rest'):
                chord = new_chord()
                voice.remove(rest)
                voice.append(chord)

    # print(etree.tostring(tree).decode())

    tree.write(
        'a.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )


### 関数 ###

# 新しくchord要素を作る
def new_chord():
    # chord要素の準備
    chord = etree.Element('Chord')
    durationType = etree.Element('durationType')
    note = etree.Element('Note')
    pitch = etree.Element('pitch')
    tpc = etree.Element('tpc')

    # 親子関係の構築
    chord.append(durationType)
    chord.append(note)
    note.append(pitch)
    note.append(tpc)

    # 要素に内容を書き込む
    durationType.text = 'whole'
    pitch.text = '60'
    tpc.text = '14'

    return chord

# パート別に適切なpitchとtpcを選ぶ関数
def choose_pitch():
    return



if __name__ == "__main__":
    main()