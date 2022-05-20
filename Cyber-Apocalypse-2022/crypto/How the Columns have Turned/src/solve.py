#!/usr/bin/env python3

def deriveKey(key):
    derived_key = []
    for i, char in enumerate(key):
        previous_letters = key[:i]
        new_number = 1
        for j, previous_char in enumerate(previous_letters):
            if previous_char > char:
                derived_key[j] += 1
            else:
                new_number += 1
        derived_key.append(new_number)
    return derived_key

def transpose(array):
    return [row for row in map(list, zip(*array))]

def flatten(array):
    return "".join([i for sub in array for i in sub])

def unflatten(string):
    BLOCK_SIZE = 15
    block_size = int(len(string) / BLOCK_SIZE)
    block_count = int(len(string) / block_size)
    ret = []
    for i in range(block_count):
        block = []
        for j in range(block_size):
            block.append(string[j + i * block_size])
        ret.append(block)
    return ret

def untwistColumnarEncrypt(encrypted, key):
    derived_key = deriveKey(key)
    width = len(key)
    twisted_key = [derived_key.index(i + 1) for i in range(width)]
    encrypted = unflatten(encrypted)
    reversed_blocks = [None]*width
    for i in range(width):
        reversed_blocks[twisted_key[i]] = encrypted[i][::-1]
    return flatten(transpose(reversed_blocks))

def main():
    encrypted = input('Encrypted text: ')
    key = input('key: ')

    print(untwistColumnarEncrypt(encrypted, key))

if __name__ == '__main__':
    main()