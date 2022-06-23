import subprocess
import os
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd


### xmlの操作に関する関数

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


# コードの再生を止める関数
def no_play(harmony_elem):
    if harmony_elem.xpath('./play'):
        harmony_elem.remove(harmony_elem.xpath('./play')[0])
    play_elem = etree.Element('play')
    play_elem.text = '0'
    harmony_elem.append(play_elem)
    return



### tpcなどの操作

# 音名から Tonal Pitch Class を取得する
def tpc(note: str):
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


# ピッチをTPCに変換
def pitch_to_tpc(pitch: int):
    if pitch % 2 == 1:
        tpc =  pitch % 12 + 8
    else:
        tpc =  pitch % 12 + 14
    return tpc

# TPCをピッチに変換
def tpc_to_pitch(tpc: int, min: int):
    if tpc % 2 == 1:
        pitch = tpc + 16
    else:
        pitch = tpc + 10
    while pitch < min:
        pitch += 12
    return pitch

# 根音とインターバルから、ピッチとTPCの配列を取得する関数
def pitches_and_tpcs(root, intervals, min=59):
    pitches = [0 for i in range(len(intervals))]
    tpcs = [0 for i in range(len(intervals))]
    root_pitch = tpc_to_pitch(root, 100)

    for i in range(len(pitches)):
        pitches[i] = intervals[i] + root_pitch

    while pitches[2] - 12 >= min:
        top = pitches.pop()
        third = top - 12
        pitches.insert(0, third)

    for i in range(len(tpcs)):
        tpcs[i] = pitch_to_tpc(pitches[i])

    return pitches, tpcs