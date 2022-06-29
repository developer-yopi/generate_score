import math
from fractions import Fraction

from lxml import etree
import pandas as pd


THIRD_MIN = 59


### xmlの操作に関する関数

# 新しいchord要素
def new_chord(length: float, pitch: int, tpc: int):
    # chord要素の準備
    chord_elem = etree.Element('Chord')
    dots_elem = etree.Element('dots')
    duration_type_elem = etree.Element('durationType')
    note_elem = etree.Element('Note')
    pitch_elem = etree.Element('pitch')
    tpc_elem = etree.Element('tpc')

    # 要素に内容を書き込む
    duration, dots = length_to_duration_and_dots(length)
    duration_type = duration_to_duration_type(duration)
    dots_elem.text = str(dots)
    duration_type_elem.text = duration_type
    pitch_elem.text = str(pitch)
    tpc_elem.text = str(tpc)

    # 親子関係の構築
    if dots:
        chord_elem.append(dots_elem)
    chord_elem.append(duration_type_elem)
    chord_elem.append(note_elem)
    note_elem.append(pitch_elem)
    note_elem.append(tpc_elem)

    return chord_elem


# 新しいrest要素
def new_rest(length: float):
    # rest要素の準備
    rest_elem = etree.Element('Rest')
    dots_elem = etree.Element('dots')
    duration_type_elem = etree.Element('durationType')
    note_elem = etree.Element('Note')

    # 要素に内容を書き込む
    duration, dots = length_to_duration_and_dots(length)
    duration_type = duration_to_duration_type(duration)
    dots_elem.text = str(dots)
    duration_type_elem.text = duration_type

    # 親子関係の構築
    if dots:
        rest_elem.append(dots_elem)
    rest_elem.append(duration_type_elem)
    rest_elem.append(note_elem)

    return rest_elem


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


# コードの再生をオフにする関数
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
        tpc = pitch % 12 + 8
    else:
        tpc = pitch % 12 + 14
    if tpc < 10:
        tpc += 12
    elif tpc > 21:
        tpc -= 12
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
def pitches_and_tpcs(root, intervals, min=THIRD_MIN):
    root_pitch = tpc_to_pitch(root, 100)

    pitches = [root_pitch + intervals[i] for i in range(3)]

    while pitches[2] - 12 >= min:
        top = pitches.pop()
        third = top - 12
        pitches.insert(0, third)

    tpcs = [pitch_to_tpc(pitches[i]+12) for i in range(3)]

    return pitches, tpcs

# chordを取得する関数
def get_chord(voice):
    chord_list = []
    position = 0
    for element in voice.xpath('./*'):
        if element.tag == 'Harmony':
            root = int(element.xpath('./root')[0].text)
            try:
                name = element.xpath('./name')[0].text
            except IndexError:
                name = None
            try:
                base = int(element.xpath('./base')[0].text)
            except IndexError:
                base = None
            chord_list.append([position, root, name, base])
        elif element.tag == 'Rest' or element.tag == 'Chord':
            duration_type = element.xpath('./durationType')[0].text
            duration = duration_type_to_duration(duration_type)
            if element.xpath('dots'):
                duration *= (2 - (1/2)**int(element.xpath('dots')[0].text))
            position += duration
        elif element.tag == 'location':
            position += float(Fraction(element.xpath('fractions')[0].text))
    return chord_list

def duration_type_to_duration(duration_type: str):
    if duration_type == 'measure' or duration_type == 'whole':
        return 1
    elif duration_type == 'half':
        return 1/2
    elif duration_type == 'quarter':
        return 1/4
    elif duration_type == 'eighth':
        return 1/8
    elif duration_type == '16th':
        return 1/16
    elif duration_type == '32nd':
        return 1/32
    elif duration_type == '64th':
        return 1/64

def duration_to_duration_type(duration: float):
    if duration == 1:
        return 'whole'
    elif duration == 1/2:
        return 'half'
    elif duration == 1/4:
        return 'quarter'
    elif duration == 1/8:
        return 'eighth'
    elif duration == 1/16:
        return '16th'
    elif duration == 1/32:
        return '32nd'
    elif duration == 1/64:
        return '64th'

def length_to_duration_and_dots(length: float):
    duration = 1.0
    while length < duration:
        duration /= 2.0
    dots = int(math.log(2.0-length/duration, 1/2))
    return duration, dots