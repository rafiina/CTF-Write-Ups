# Inside the Matrix
Category: Crypto
Difficulty: Easy

## The Challenge

```python
from sage.all_cmdline import *
# from utils import ascii_print
import os

FLAG = b"HTB{????????????????????}"
assert len(FLAG) == 25


class Book:

    def __init__(self):
        self.size = 5
        self.prime = None

    def parse(self, pt: bytes):
        print(pt)
        pt = [b for b in pt]
        print(pt)
        print(GF(self.prime), end='\n\n')
        print(matrix(GF(self.prime), self.size, self.size, pt))
        print('\n\n')
        return matrix(GF(self.prime), self.size, self.size, pt)

    def generate(self):
        key = os.urandom(self.size**2)
        return self.parse(key)

    def rotate(self):
        self.prime = random_prime(2**6, False, 2**4)

    def encrypt(self, message: bytes):
        self.rotate()
        key = self.generate()
        print(message, end='\n\n')
        message = self.parse(message)
        print(message, end='\n\n')
        ciphertext = message * key
        print(key, end='\n\n')
        print(ciphertext, end='\n\n')
        return ciphertext, key


def menu():
    print("Options:\n")
    print("[L]ook at page")
    print("[T]urn page")
    print("[C]heat\n")
    option = input("> ")
    return option


def main():
    book = Book()
    ciphertext, key = book.encrypt(FLAG)
    page_number = 1

    while True:
        option = menu()
        if option == "L":
            # ascii_print(ciphertext, key, page_number)
            print(ciphertext, key, page_number)
        elif option == "T":
            ciphertext, key = book.encrypt(FLAG)
            page_number += 2
            print()
        elif option == "C":
            print(f"\n{list(ciphertext)}\n{list(key)}\n")
        else:
            print("\nInvalid option!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
```

## The Prompt

We are presented with a prompt to look at a page, turn a page, or cheat.  

Looking at a page draws some nice ascii art (at least for the original challenge -- we get a simpler print here) showing a key and cipher.

Cheating prints the key and cipher in a more straightforward manner.  Handy for easy parsing.

Turning the page generates a new pair of cipher and key for us to use.

## Understanding the Script

This uses the sagemath package (install with package manager, not pip...it's quite large) and utilizes Martrices over Finite Fields:
https://www.ast.cam.ac.uk/sites/default/files/CATAM_PartIB_2018_2019_1pt1.pdf

No need to read the article.  The parse function in the challenge just converts the flag and key bytes to an array of decimals:

`b'HTB{????????????????????}'` -> `[72, 84, 66, 123, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 125]`

Then converts each number to a new number modulo some prime (say 43).  This is what it means by 'over Finite Fields':
`[72, 84, 66, 123, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 125]` -> `[29 41 23 37 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 39]`

Then we get this final list as a square matrix.

```
Example Flag matrix
[29 41 23 37 20]
[20 20 20 20 20]
[20 20 20 20 20]
[20 20 20 20 20]
[20 20 20 20 39]
```

```
Example key matrix
[39  9 26 16 29]
[17 16 21 29 33]
[22 34 22 39 41]
[10 31  8 38 33]
[10 28 23 41  7]
```

We multiple these together Flag * Key (order matters, because matrices):

![Matrix Multiplication](images/matrix_mult.png)

```
2904    3406    2877    4776    4498
1960    2360    2000    3260    2860
1960    2360    2000    3260    2860
1960    2360    2000    3260    2860
2150    2892    2437    4039    2993
```

Since these matrices are over a finite field, we adjust (field size is still 43 for this example, so modulo 43)

```
Ciphertext Matrix
[23  9 39  3 26]
[25 38 22 35 22]
[25 38 22 35 22]
[25 38 22 35 22]
[ 0 11 29 40 26]
```

## Reversing the Process

We are given the Key matrix and this final Matrix and need to extract the message (flag)
F * K = M
F * K * K^(-1) = M * K^(-1)
F = M * K^(-1)

Solving this, we get

```
Example F
[  -220597/324027     64342/108009   1109476/324027  -1111252/324027    -17383/108009]
[   211709/648054 -1428871/1080090  2372704/1620135  -702047/3240270   507247/1080090]
[   211709/648054 -1428871/1080090  2372704/1620135  -702047/3240270   507247/1080090]
[   211709/648054 -1428871/1080090  2372704/1620135  -702047/3240270   507247/1080090]
[    -19835/24002    330481/120010     -36838/60005    -69161/120010     56213/120010]
```

We just need to know our field size.  We know what it is for this example, 43, which brings us back to the flag matrix we started with.

```
Flag Matrix
[29 41 23 37 20]
[20 20 20 20 20]
[20 20 20 20 20]
[20 20 20 20 20]
[20 20 20 20 39]
```

Finally, we had some multiple of our field size to each member of this matrix until we get a value that is in the range of the printable ASCII characters [32-126].

We do not know the field size, we will need to determine that.

There are a couple key things to notice.

1) By definition the field size of our matrix must be a prime power (p^k for some prime and some integer k) and, per the server code, between 2^4 and 2^6 (see the rotate() function).
2) We may get more than one possible value for a given item.  For example, taking the first item `29` and pretend our field size is `27` (3^3), we see:

```
29 + 1 * 27 = 56
29 + 2 * 27 = 83
29 + 3 * 27 = 110
```

This means the 29 could represent any of the characters `8`, `S`, or `n`.

## The algorithms

### Primary algorithm

1) Solve matrix equation for our flag matrix
2) Determine key size
3) Determine character space for each item in flag matrix
4) Repeat until we have only one possibility for each flag character

### Solve matrix

Sage math makes this trivial.  Just one line:

```python
flag = key.solve_left(msg)
```

### Determine Key Size

Relevant function(s) in solution: `get_field_size`, `find_possible_field_sizes`

`find_possible_field_sizes` just generates all the possible sizes.  There aren't many.

`get_field_size` is the main part.

We loop through each possible field size.  In the loop, we apply the field size to the key and extract the first value.  We then add multiples of the field size to the extracted value, keeping any valid value for a printable char.

To save time, we use the known fact that first character is 72 (`H`).  If we end up with more than one possible key, we will later just turn the page and start with a new key/cipher.

### Determine character space

Relevant function(s) in solution: `generate_flag`

We loop through every flag matrix entry, generating possible characters with the same formula used in the previous step.

```
Flag String: 
[
  ['H', 's'], 
  [')', 'T'], 
  ['B', 'm'], 
  ['%', 'P', '{'], 
  ['A', 'l'], 
  ['0', '['], 
  ['0', '['], 
  ['@', 'k'], 
  ['4', '_'], 
  ['@', 'k'], 
  ['I', 't'], 
  ['4', '_'], 
  ['7', 'b'], 
  ['=', 'h'], 
  ['3', '^'], 
  ['4', '_'], 
  ['H', 's'], 
  ['I', 't'], 
  ['4', '_'], 
  ['G', 'r'], 
  ['H', 's'], 
  ['!', 'L', 'w'], 
  ['!', 'L', 'w'], 
  ['!', 'L', 'w'], 
  ["'", 'R', '}']
]
```

## Putting it Together

Notice in the example, we have more than one possible character for some positions in the flag.  So we repeat the above algorithms on new key/cipher pairs, using the `find_flag_intersection` function at each step to reduce the possibilities for each position.  Eventually, we get a unique flag.