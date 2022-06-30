import glob

from lxml import etree
import pandas as pd

import scoremodule as sm


BASE_MIN = 40   # Bass の最低音


def main():

    # コードのデータフレームを読み込む
    df_chord = pd.read_csv('csv/chord.csv', index_col='name')

    # ファイル名を取得   
    path = './score/'
    mscx = glob.glob(path + 'c.mscx')[0]
    
    # mscxを解析
    tree = etree.parse(mscx)

    # リードの段のコードを取得
    chord_list = []
    staffs = tree.xpath('//Staff')
    lead_staff = staffs[len(staffs)//2]
    for voice in lead_staff.xpath('./Measure/voice'):  # 小節
        chord_list.append(sm.get_chord(voice))
        for harmony in voice.xpath('./Harmony'):
            sm.no_play(harmony)  # コードの再生をオフにする

    # コーラス
    for i, staff in enumerate(staffs[len(staffs)//2+1:len(staffs)//2+5]):
        for j, voice in enumerate(staff.xpath('./Measure/voice')):  # 小節
            for rest in voice.xpath('./Rest'):  # 休符の削除
                voice.remove(rest)
            for chord in voice.xpath('./Chord'):  # 音符の削除
                voice.remove(chord)
            # 音符の入力
            for k, chord in enumerate(chord_list[j]):
                if not chord:
                    voice.append(sm.new_rest('measure'))
                    break
                if k == 0 and chord[0] != 0:
                    voice.append(sm.new_rest(chord[0]))
                if k == len(chord_list[j]) - 1:
                    length = 1 - chord[0]
                else:
                    length = chord_list[j][k+1][0] - chord[0]
                root, name, base = chord[1:]
                if not name:
                    name = 'M'  # メジャーコードを識別できるようにする
                if not base:
                    base = root  # 基音が存在しない場合、基音は根音とする
                # ベースの音符入力
                if i == 3:
                    pitch = sm.tpc_to_pitch(base, BASE_MIN)
                    voice.append(sm.new_chord(length, pitch, base))
                # コーラスの音符入力
                else:
                    intervals = df_chord.loc[name]  # コード名に対応した和音の構成音のリストを取得
                    pitches, tpcs = sm.pitches_and_tpcs(root, intervals)
                    voice.append(sm.new_chord(length, pitches[2-i], tpcs[2-i]))

    # ファイル出力
    tree.write(
        './score/d.mscx',
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )

    return


if __name__ == "__main__":
    main()
