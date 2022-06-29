import sys

import requests
from bs4 import BeautifulSoup


def main(argv):

    if len(argv) == 2:
        url = argv[1]
    else:
        url = 'https://gakufu.gakki.me/m/data/M00211.html'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    tag_obj = soup.find_all('span', class_='cd_fontpos')
    chord_list = [
        chord.text
        .replace('â\x99\xad', 'b')  # ♭ を b に置換
        .replace('ï¼\x83', '#')     # ＃ を # に置換
        .replace('on', '/')         # on を / に置換
        for chord in tag_obj
    ]

    # chord.txtに出力
    with open('chord.txt', 'w') as f:
        chords = [chord + '\n' for chord in chord_list]
        f.writelines(chords)

    return


if __name__ == '__main__':
    main(sys.argv)