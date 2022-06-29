import subprocess
import os
from zipfile import ZipFile
import glob

from lxml import etree

import scoremodule as sm


BASE_MIN = 40   # Bass の最低音


def main():

    # ファイル名を取得
    path = './score/'
    mscz = glob.glob(path + '*.mscz')[0]                    
    title = os.path.basename(mscz).replace('.mscz', '')       

    # msczをunzipし、mscxをtmpディレクトリに格納
    tmp_dir = './tmp/'
    subprocess.run(['mkdir', tmp_dir])
    with ZipFile(mscz, 'r') as mscx_zip:
        file_names = mscx_zip.namelist()
        for file_name in file_names:
            mscx_zip.extract(file_name, tmp_dir)
            if file_name.endswith('.mscx'):
                mscx_zip.extract(file_name, tmp_dir)
                mscx = tmp_dir + title + '.mscx'
                tree = etree.parse(mscx)
    subprocess.run(['rm', '-r', './tmp/'])

    # chord.txtからコードの情報を取得
    with open('chord.txt', 'r') as f:
        chords = f.readlines()
        chord_list = [chord.replace('\n', '') for chord in chords]

    staffs = tree.xpath('//Staff')
    for i, staff in enumerate(staffs[len(staffs)//2:]):  # パート
        for j, voice in enumerate(staff.xpath('./Measure/voice')):  # 小節
            chord = chord_list[j]
            root, name, base = sm.separate_chord(chord)
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                if i == 0:  # 一番上の段にのみコード情報を入れる
                    voice.insert(k, sm.new_harmony(root, name, base))
                elif i == 4:  # Bass を入力
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    if base:
                        voice.append(sm.new_chord(length=1, pitch=sm.tpc_to_pitch(base, BASE_MIN), tpc=base))
                    else:
                        voice.append(sm.new_chord(length=1, pitch=sm.tpc_to_pitch(root, BASE_MIN), tpc=root))

    # ファイル出力
    tree.write(
        path + 'a.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )


if __name__ == "__main__":
    main()