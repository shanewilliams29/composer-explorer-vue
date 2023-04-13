import json
from plotapi import Chord 


with open('../data/matrix/composer_list.json', 'r') as file:
    composer_list = json.load(file)


def load_artists(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def common_artists_count(artists1, artists2):
    return len(set(artists1) & set(artists2))

matrix = []
for composer in composer_list:
    i = 0
    matrix_x = []
    while i < len(composer_list):
        artists1 = load_artists(f'../data/matrix/{composer}.json')
        artists2 = load_artists(f'../data/matrix/{composer_list[i]}.json')
        count = common_artists_count(artists1, artists2)
        matrix_x.append(count)
        i += 1
    matrix.append(matrix_x)

print(composer_list)
print(matrix)

Chord(matrix, composer_list).show()

#print(f'Number of artists in common between {composer} and {composer_list[i]}: {count}')