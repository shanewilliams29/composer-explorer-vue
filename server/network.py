import json
import csv
import math

cutoff = int(input("Enter number of composers cutoff: "))


with open('../data/network/composer_list.json', 'r') as file:
    composer_list = json.load(file)


def load_artists(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def common_artists_count(artists1, artists2):
    return len(set(artists1) & set(artists2))


composer_weights = {}
for composer in composer_list:
    artist_list = load_artists(f'../data/network/{composer}.json')
    composer_weights[composer] = len(artist_list)

with open("../data/network/composer_weights.json", 'w', encoding='utf8') as outfile:
    json.dump(composer_weights, outfile, ensure_ascii=False)    

# composer_sizes = {}
matrix = []
for composer in composer_list:
    temp_matrix = []
    i = 0
    while i < len(composer_list):
        artists1 = load_artists(f'../data/network/{composer}.json')
        artists2 = load_artists(f'../data/network/{composer_list[i]}.json')
        
        if composer == composer_list[i]:
            # composer_sizes[composer] = len(artists1)
            i += 1
            continue

        count = common_artists_count(artists1, artists2)
        count_normalized = count/math.sqrt(composer_weights[composer_list[i]])*100
        temp_matrix.append([composer, composer_list[i], count_normalized])
        i += 1

    sorted_list = sorted(temp_matrix, key=lambda x: x[2], reverse=True)[:cutoff]
    
    matrix.extend(sorted_list)

with open('../data/network/matrix.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Source', 'Target', 'Weight'])
    for row in matrix:
        writer.writerow(row)

print("Matrix saved as /data/network/matrix.csv!")

# with open("../data/matrix/composer_weights.json", 'w', encoding='utf8') as outfile:
#     json.dump(composer_sizes, outfile, ensure_ascii=False)

#print(matrix)
#Chord(matrix, composer_list).show()

#print(f'Number of artists in common between {composer} and {composer_list[i]}: {count}')