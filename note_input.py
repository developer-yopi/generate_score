import os
import subprocess
import glob

from lxml import etree
import pandas as pd

import scoremodule as sm


def main():

    # コードのデータフレームを読み込む
    df_chord = pd.read_csv('csv/chord.csv', index_col='name')

    # chord.txtからコードの情報を取得
    with open('chord.txt', 'r') as f:
        chords = f.readlines()
        chord_list = [chord.replace('\n', '') for chord in chords]

    # ファイル名を取得   
    path = './score/'
    mscx = glob.glob(path + 'a.mscx')[0]
    
    tree = etree.parse(mscx)
    staffs = tree.xpath('//Staff')
    for i, staff in enumerate(staffs[len(staffs)//2:]):  # パート
        for j, voice in enumerate(staff.xpath('./Measure/voice')):  # 小節
            for harmony in voice.xpath('./Harmony'):
                sm.no_play(harmony)  # コードの再生をオフにする
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                root, name, base = sm.separate_chord(chord_list[j])
                if not name:
                    name = 'M'  # メジャーコードを識別できるようにする
                intervals = df_chord.loc[name]  # コード名に対応した和音の構成音のリストを取得
                pitches, tpcs = sm.pitches_and_tpcs(root, intervals)
                # Top, 2nd, 3rd の入力
                if 1 <= i <= 3:
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    voice.append(sm.new_chord(pitch=pitches[3-i], tpc=tpcs[3-i]))

    # ファイル出力
    tree.write(
        './score/b.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )

    return


if __name__ == "__main__":
    main()
