import os
import subprocess

from lxml import etree
import pandas as pd

import scoremodule as sm


def main():
    df_chord = pd.read_csv('csv/chord.csv', index_col='name')
    # print(df_chord)

    # chord.txtからコードの情報を取得
    with open('chord.txt', 'r') as f:
        chords = f.readlines()
        chord_list = [chord.replace('\n', '') for chord in chords]

    # ファイル名を取得
    file_list = os.listdir()
    for file in file_list:
        if file.endswith('a.mscx'):
            mscx = file
            title = mscx.replace('.mscx', '')
            break 
    
    tree = etree.parse(mscx)
    staffs = tree.xpath('//Staff')
    for i, staff in enumerate(staffs[len(staffs)//2:]):  # パート
        for j, voice in enumerate(staff.xpath('./Measure/voice')):  # 小節
            for harmony in voice.xpath('./Harmony'):
                sm.no_play(harmony)
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                root, name, base = sm.separate_chord(chord_list[j])
                if not name:
                    name = 'M'
                intervals = df_chord.loc[name]
                print(df_chord.loc[name])
                pitches, tpcs = sm.pitches_and_tpcs(root, intervals)
                if 1 <= i and i <= 3:
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    voice.append(sm.new_chord(pitch=pitches[3-i], tpc=tpcs[3-i]))

    # ファイル出力
    tree.write(
        './b.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )

    return


if __name__ == "__main__":
    main()
