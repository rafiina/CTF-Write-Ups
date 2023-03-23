#!/usr/bin/env python3

import sage.all_cmdline as sage
import socket
from ast import literal_eval

# Matrix size
SIZE = 5
# Chars possible in flag
POSSIBLE_CHARS = list(range(32, 127))
SERVER_ADDRESS = "142.93.35.133"
SERVER_PORT = 30600

def report(msg, key, flag, field_size, flag_string):
    print(f'Message Matrix:\n{msg}\n')
    print(f'Key Matrix:\n{key}\n')
    print(f'Flag Matrix Inverse:\n{flag}\n')
    print(f'Found field size: {field_size}', end='\n\n')
    print(f'Flag array: {flag.list()}', end='\n\n')
    print(f'Flag String: {flag_string}')

def flatten(matrix): 
    return [val for row in matrix for val in row]


def get_field_size(flag):
    field_sizes_found = dict()
    chars_found = set()

    for n in find_possible_field_sizes():
        field_sizes_found[n] = set()
        try:
            # Apply field size
            m = sage.matrix(sage.GF(n), flag)
            m = int(m[0][0])
            if m == 0:
                continue 
        except Exception as e:
            continue
        x = 1
        while(True):
            result = n * x + m
            if result in POSSIBLE_CHARS:
                field_sizes_found[n].add(chr(result))
                chars_found.add(chr(result))
            if m * x > max(POSSIBLE_CHARS):
                break
            x += 1

    # We find more possible sizes than I expected, so I'm cheating
    # and using the known value of 'H' to filter
    filtered_sizes = {k: v for k, v in field_sizes_found.items() if v != set() and 'H' in v}

    return filtered_sizes

def find_possible_field_sizes():
    # Our field size from the source code is 16 <= n <= 64
    # They must also be prime powers -- some p^k for prime p and integer k
    # Our fieldsize must also be at least 1 higher than the largest value in our key and msg
    # Use sage to create a prime power generator (NN is a sage class)
    p = (q for q in sage.NN if sage.is_prime_power(q))
    possible_field_sizes = set()
    n = 0

    while n <= 2**6:
        n = next(p)
        if n >= 2**4:
            possible_field_sizes.add(n)

    return possible_field_sizes

def generate_flag(flag, field_size):
    flag_string = []
    for char in flag.list():
        chars = []
        for x in range((max(POSSIBLE_CHARS) // field_size) + 1):
            if (x * field_size + char) in POSSIBLE_CHARS:
                chars.append(chr(x*field_size + char))
        flag_string.append(chars)

    return flag_string

def decode_message(msg: list, key: list) -> list:
    msg = sage.matrix(SIZE, SIZE, msg)
    key = sage.matrix(SIZE, SIZE, key)

    flag = key.solve_left(msg)

    field_sizes = get_field_size(flag)
    if len(field_sizes) > 1:
        raise Exception("More than one possible field size.  Skipping.")

    # Trick to get value from single key/value dict
    field_size = list(field_sizes)[0]

    # Apply field size
    flag = sage.matrix(sage.GF(field_size), flag)

    # Recreate matrix over normal integer so we can multiple by scalars
    flag = sage.matrix(sage.ZZ, flag)

    # Find possible values for each char in flag
    flag_string = generate_flag(flag, field_size)

    report(msg, key, flag, field_size, flag_string)

    return flag_string

def get_next_msg(client):
    client.sendall("C\n".encode())
    res = client.recv(1024).decode()
    res = res.split('\n')

    return literal_eval(res[1]), literal_eval(res[2])

def turn_page(client):
    client.sendall("T\n".encode())
    res = client.recv(1024)

def find_flag_intersection(flag, next_flag):
    if flag == []:
        return next_flag
    
    ret = []
    for char in range(len(flag)):
        ret.append([c for c in flag[char] if c in next_flag[char]])

    return ret

def check_flag(flag):
    return flag and all([len(char) == 1 for char in flag])

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_ADDRESS, SERVER_PORT))
    res = client.recv(1024).decode()

    flag = []
    while (not check_flag(flag)):
        print("==============================\n")
        print("Processing new message and key\n")
        msg, key = get_next_msg(client)
        try:
            next_flag = decode_message(msg, key)
        except Exception as e:
            print(e)
            continue
        flag = find_flag_intersection(flag, next_flag)
        turn_page(client)
        print("\n\n==============================\n\n")


    print(''.join([i[0] for i in flag]))

if __name__ == '__main__':
    main()
