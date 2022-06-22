import os
import subprocess

from lxml import etree
import pandas as pd
import generate_score as gs

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
            for k, rest in enumerate(voice.xpath('./Rest')):  # 休符
                root, name, base = gs.separate_chord(chord_list[j])
                if not name:
                    name = 'M'
                intervals = df_chord.loc[name]
                print(df_chord.loc[name])
                pitches, tpcs = pitches_and_tpcs(root, intervals)
                if 1 <= i and i <= 3:
                    # 休符を消し音符を入力
                    voice.remove(rest)
                    voice.append(gs.new_chord(pitch=pitches[3-i], tpc=tpcs[3-i]))

    # ファイル出力
    tree.write(
        # mscx,
        './b.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )

    return


def pitch_to_tpc(pitch: int):
    if pitch % 2 == 1:
        tpc =  pitch % 12 + 8
    else:
        tpc =  pitch % 12 + 14

    return tpc

def tpc_to_pitch(tpc: int, min: int):
    if tpc % 2 == 1:
        pitch = tpc + 16
    else:
        pitch = tpc + 10
    
    while pitch < min:
        pitch += 12

    return pitch

def pitches_and_tpcs(root, intervals):
    pitches = [0 for i in range(len(intervals))]
    tpcs = [0 for i in range(len(intervals))]
    root_pitch = tpc_to_pitch(root, 48)

    for i in range(len(pitches)):
        pitches[i] = intervals[i] + root_pitch

    for i in range(len(tpcs)):
        tpcs[i] = pitch_to_tpc(pitches[i])

    return pitches, tpcs
        


if __name__ == "__main__":
    main()
