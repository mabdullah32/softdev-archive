import sys
import math


def freq(letters):
    result = [0.0] * 26
    denom = 0.0

    for letter in letters:
        if letter.isalpha():
            letter = letter.upper()
            result[ord(letter) - ord('A')] += 1.0
            denom += 1.0

    final = [i/denom for i in result]

    return final

with open("alice_in_wonderland.txt") as f:
    sfreq = freq(f.read())

def dist(set1, set2):
    sum = 0.0
    for i in range(len(set1)):
        sum += (set1[i] - set2[i])**2
    
    return math.sqrt(sum)

def decode(message, sFreq):
    final_dist = 10
    final_string = ""
    best_shift = 0
    for i in range(26):
        a = ""
        for j in message:
            if j.isalpha():
                if j.isupper():
                    shift = ((ord(j) - ord('A') + i) % 26)
                    a += chr(shift + ord('A'))
                else:
                    shift = ((ord(j) - ord('a') + i) % 26)
                    a += chr(shift + ord('a'))


            else:
                a += j
            
        attempt_distance = dist(freq(a), sFreq)

        if attempt_distance < final_dist:
            final_dist = attempt_distance
            final_string = a
            best_shift = i

    atbash = ""
    for ch in message:
        if ch.isupper():
            atbash += chr(ord('Z') - (ord(ch) - ord('A')))
        elif ch.islower():
            atbash += chr(ord('z') - (ord(ch) - ord('a')))
        else:
            atbash += ch

    for i in range(26):
        a = ""
        for j in atbash:
            if j.isalpha():
                if j.isupper():
                    a += chr(((ord(j) - ord('A') + i) % 26) + ord('A'))
                else:
                    a += chr(((ord(j) - ord('a') + i) % 26) + ord('a'))
            else:
                a += j
            
        attempt_distance = dist(freq(a), sFreq)

        if attempt_distance < final_dist:
            final_dist = attempt_distance
            final_string = a
            best_shift = i

    return [final_string, best_shift]

def split_files(text, key_length):
    lists = []
    [lists.append([]) for i in range(key_length)]

    for i, char in enumerate(text):
        if char.isalpha():
            lists[i % key_length].append(char)
    
    final_list = []
    for list in lists:
        final_list.append("".join(list))
    return final_list

def merge(piles, total_length):
    result = []
    indices = [0] * len(piles)
    for i in range(total_length):
        pile_idx = i % len(piles)
        result.append(piles[pile_idx][indices[pile_idx]])
        indices[pile_idx] += 1
    return "".join(result)

def encrypt(message, key):
    final = ""
    result = []
    key_index = 0
    for char in message:
        if char.isalpha():
            char = char.upper()
            shift = ord(key[key_index % len(key)]) - ord('A')
            a = ((ord(char) + shift) - ord('A')) % 26
            result.append(chr(a + ord('A')))
            key_index += 1
        
    return final.join(result)


def decrypt(message, key):
    result = []
    key_index = 0
    for char in message:
        char = char.upper()
        if 'A' <= char <= 'Z':
            shift = -(ord(key[key_index % len(key)]) - ord('A'))
            a = (ord(char) + shift - ord('A')) % 26
            result.append(chr(a + ord('A')))
            key_index += 1

    return "".join(result)

def crack(message):
    best_dist = 10
    best_message = ""
    for i in range(1, 13):
        piles = split_files(message, i)
        decoded_piles = [decode(pile, sfreq)[0] for pile in piles]
        result = merge(decoded_piles, len(message))
        attempt_distance = dist(freq(result), sfreq)
        if attempt_distance < best_dist:
            best_dist = attempt_distance
            best_message = result
            
    return best_message

def getkey(message):
    
    best_dist = 10
    best_keylength = 1
    best_shifts = []
    for i in range(1, 13):
        piles = split_files(message, i)
        decoded = [decode(pile, sfreq) for pile in piles]
        decoded_piles = [d[0] for d in decoded]
        shifts = [d[1] for d in decoded]

        result = merge(decoded_piles, len(message))
        attempt_distance = dist(freq(result), sfreq)

        if attempt_distance < best_dist:
            best_dist = attempt_distance
            best_shifts = shifts
            best_keylength = i

    return "".join(chr(ord('A') + (26 - shift) % 26) for shift in best_shifts)

if sys.argv[1] == 'encode':

    filename = sys.argv[2]
    keyfile = sys.argv[3]
    with open (filename) as f:
        contents = f.read().strip().replace('\r', '').replace('\n', '')
    with open (keyfile) as f:
        key_contents = f.read().strip().replace('\r', '').replace('\n', '')
    
    print(encrypt(contents, key_contents))

elif sys.argv[1] == 'decode':

    filename = sys.argv[2]
    keyfile = sys.argv[3]
    with open (filename, 'r') as f:
        contents = f.read().strip().replace('\r', '').replace('\n', '')
    with open (keyfile, 'r') as f:
        key_contents = f.read().strip().replace('\r', '').replace('\n', '')
    
    print(decrypt(contents, key_contents))

elif sys.argv[1] == 'crack':

    filename = sys.argv[2]

    with open (filename, 'r') as f:
        contents = f.read().strip().replace('\r', '').replace('\n', '')

    print(crack(contents))

elif sys.argv[1] == 'getkey':
    filename = sys.argv[2]

    with open(filename, 'r') as f:
        contents = f.read().strip().replace('\r', '').replace('\n', '')

    print(getkey(contents))