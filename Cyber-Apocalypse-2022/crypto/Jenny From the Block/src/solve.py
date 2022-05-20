#!/usr/bin/env python3

from hashlib import sha256

BLOCK_SIZE = 32

def get_encrypted_message():
    msg = input("Enter the encrypted message: ")
    msg = bytes.fromhex(msg)
    while (len(msg) % BLOCK_SIZE != 0):
        print("Invalid message.  Must have a block size of 32 bytes.")
        msg = input("Enter the encrypted message: ")
    return msg

def get_next_sha(block, enc_block):
    return sha256(enc_block + block).digest()

def get_first_sha(block, val):
    secret = []
    for i in range(len(block)):
        byte = val[i] - block[i]
        if (byte < 0):
                byte += 256
        secret.append(hex(byte).replace('0x',''))
    secret = ''.join([x.zfill(2) for x in secret])
    return bytes.fromhex(secret)

def get_next_block(sha, encrypted):
    block = []
    for i in range(len(sha)):
        byte = encrypted[i] - sha[i]
        if (byte < 0):
                byte += 256
        block.append(hex(byte).replace('0x',''))
    block = ''.join([x.zfill(2) for x in block])
    return bytes.fromhex(block)

def main():
    first_known_block = bytes.fromhex('436f6d6d616e642065786563757465643a20636174207365637265742e747874') # Command executed: cat secret.txt
    msg = get_encrypted_message()
    encrypted_blocks = [msg[i:i+BLOCK_SIZE] for i in range(0, len(msg), BLOCK_SIZE)]
    blocks = []
    sha_list = [get_first_sha(first_known_block, encrypted_blocks[0])]
    blocks.append(get_next_block(sha_list[0], encrypted_blocks[0]))

    for i in range(1, len(encrypted_blocks)):
        next_sha = get_next_sha(blocks[i - 1], encrypted_blocks[i - 1])
        sha_list.append(next_sha)
        blocks.append(get_next_block(sha_list[i], encrypted_blocks[i]))

    print(''.join([x.decode() for x in blocks]))

if __name__ == "__main__":
    main()