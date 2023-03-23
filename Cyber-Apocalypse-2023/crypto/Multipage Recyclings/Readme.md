# Multipage Recyclings

Category: Crypto
Difficulty: Easy

## The Challenge

The script:

```python
#!/usr/bin/env python3

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random, os

FLAG = b'HTB{??????????????????????}'


class CAES:

    def __init__(self):
        self.key = os.urandom(16)
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def blockify(self, message, size):
        return [message[i:i + size] for i in range(0, len(message), size)]

    def xor(self, a, b):
        return b''.join([bytes([_a ^ _b]) for _a, _b in zip(a, b)])

    def encrypt(self, message):
        iv = os.urandom(16)

        ciphertext = b''
        plaintext = iv

        blocks = self.blockify(message, 16)
        for block in blocks:
            ct = self.cipher.encrypt(plaintext)
            encrypted_block = self.xor(block, ct)
            ciphertext += encrypted_block
            plaintext = encrypted_block

        return ciphertext

    def leak(self, blocks):
        r = random.randint(0, len(blocks) - 2)
        leak = [self.cipher.encrypt(blocks[i]).hex() for i in [r, r + 1]]
        return r, leak


def main():
    aes = CAES()
    message = pad(FLAG * 4, 16)

    ciphertext = aes.encrypt(message)
    ciphertext_blocks = aes.blockify(ciphertext, 16)

    r, leak = aes.leak(ciphertext_blocks)

    with open('output.txt', 'w') as f:
        f.write(f'ct = {ciphertext.hex()}\nr = {r}\nphrases = {leak}\n')

if __name__ == "__main__":
    main()
```

Our given output:

```python
ct = bc9bc77a809b7f618522d36ef7765e1cad359eef39f0eaa5dc5d85f3ab249e788c9bc36e11d72eee281d1a645027bd96a363c0e24efc6b5caa552b2df4979a5ad41e405576d415a5272ba730e27c593eb2c725031a52b7aa92df4c4e26f116c631630b5d23f11775804a688e5e4d5624
r = 3
phrases = ['8b6973611d8b62941043f85cd1483244', 'cf8f71416111f1e8cdee791151c222ad']
```

## Understanding the script

The flag is repeated four times with padding to fit a 16 byte block size.

Each plaintext block is encrypted by applying AES encryption to the result of the previous iteration and then xoring it with the current block.  The first iteration just uses a block of random chars run through AES.

## Reversing the Process

The takes two blocks of the final cipher text, AES encrypts them with the same key, and gives them back to us.

If we xor these with the correct blocks of the cipher text, we will get pieces of the original plaintext back.

Unfortunately, I don't understand enough about AES, ECB, or encryption in general to explain why this works.  I've got some homework to do!

## Solution

```python
#!/usr/bin/env python3
r = 3
phrases = ['8b6973611d8b62941043f85cd1483244', 'cf8f71416111f1e8cdee791151c222ad']
msg_blocks = ['bc9bc77a809b7f618522d36ef7765e1c', 'ad359eef39f0eaa5dc5d85f3ab249e78', '8c9bc36e11d72eee281d1a645027bd96', 'a363c0e24efc6b5caa552b2df4979a5a', 'd41e405576d415a5272ba730e27c593e', 'b2c725031a52b7aa92df4c4e26f116c6', '31630b5d23f11775804a688e5e4d5624']
vals = [(int(phrases[i], 16) ^ int(msg_blocks[i+r+1], 16)) for i in range(2)]
[bytes.fromhex(f'{i:x}') for i in vals]
```