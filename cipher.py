import hashlib
import random
import string

ALPHABET = string.ascii_uppercase

def seed_from_time(timestr):
    return int(hashlib.sha256(timestr.encode()).hexdigest(),16)

def generate_rotor(seed):
    random.seed(seed)
    letters=list(ALPHABET)
    random.shuffle(letters)
    return dict(zip(ALPHABET,letters))

def invert_rotor(rotor):
    return {v:k for k,v in rotor.items()}

def plugboard(seed):
    random.seed(seed+999)
    letters=list(ALPHABET)
    random.shuffle(letters)

    plug={}
    for i in range(0,10,2):
        a=letters[i]
        b=letters[i+1]
        plug[a]=b
        plug[b]=a

    return plug

def swap(letter,plug):
    return plug.get(letter,letter)

def encrypt(text,timestamp):

    seed=seed_from_time(timestamp)

    r1=generate_rotor(seed)
    r2=generate_rotor(seed+1)
    r3=generate_rotor(seed+2)

    plug=plugboard(seed)

    result=""

    for ch in text.upper():

        if ch not in ALPHABET:
            result+=ch
            continue

        ch=swap(ch,plug)
        ch=r1[ch]
        ch=r2[ch]
        ch=r3[ch]

        result+=ch

    return result


def decrypt(text,timestamp):

    seed=seed_from_time(timestamp)

    r1=generate_rotor(seed)
    r2=generate_rotor(seed+1)
    r3=generate_rotor(seed+2)

    r1=invert_rotor(r1)
    r2=invert_rotor(r2)
    r3=invert_rotor(r3)

    plug=plugboard(seed)

    result=""

    for ch in text.upper():

        if ch not in ALPHABET:
            result+=ch
            continue

        ch=r3[ch]
        ch=r2[ch]
        ch=r1[ch]
        ch=swap(ch,plug)

        result+=ch

    return result