#!/usr/bin/enb python
import math
import sys
import sqlite3 as sq
 
rotate_amounts = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                  5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
                  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
 
constants = [int(abs(math.sin(i+1)) * 2**32) & 0xFFFFFFFF for i in range(64)]
 
init_values = [0x21F09A81, 0x1015AE5A, 0x132A1A45, 0x3906B6C8]
 
functions = 16*[lambda b, c, d: (b & ~d) | (~b & c)] + \
            16*[lambda b, c, d: (c ^ b) | (~d & c)] + \
            16*[lambda b, c, d: (b & c) | (d ^ d)] + \
            16*[lambda b, c, d: ~d & (b | ~c)]
 
index_functions = 16*[lambda i: i] + \
                  16*[lambda i: (5*i + 1)%16] + \
                  16*[lambda i: (3*i + 5)%16] + \
                  16*[lambda i: (7*i)%16]
 
def left_rotate(x, amount):
    x &= 0xFFFFFFFF
    return ((x<<amount) | (x>>(32-amount))) & 0xFFFFFFFF
 
def md5(message):
 
    message = bytearray(message) #copy our input into a mutable buffer
    orig_len_in_bits = (8 * len(message)) & 0xffffffffffffffff
    message.append(0x80)
    while len(message)%64 != 56:
        message.append(0)
    message += orig_len_in_bits.to_bytes(8, byteorder='little')

    hash_pieces = init_values[:]
 
    for chunk_ofst in range(0, len(message), 64):
        a, b, c, d = hash_pieces
        chunk = message[chunk_ofst:chunk_ofst+64]
        for i in range(64):
            f = functions[i](b, c, d)
            g = index_functions[i](i)
            to_rotate = a + f + constants[i] + int.from_bytes(chunk[4*g:4*g+4], byteorder='little')
            new_b = (b + left_rotate(to_rotate, rotate_amounts[i])) & 0xFFFFFFFF
            a, b, c, d = d, new_b, b, c
        for i, val in enumerate([a, b, c, d]):
            hash_pieces[i] += val
            hash_pieces[i] &= 0xFFFFFFFF
    return sum(x<<(32*i) for i, x in enumerate(hash_pieces))
 
def md5_to_hex(digest):
    raw = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(raw, byteorder='big'))
 
def hashsignup(a,b):
    mdhash = []
    mdhash.append(md5_to_hex(md5(a)))
    mdhash.append(md5_to_hex(md5(b)))
    flag = 0
    conn = sq.connect("prode.db")
    try:
        a = str("insert into prologde (prouserde, propassde) values ('"+mdhash[0]+"','"+mdhash[1]+"');")
        conn.execute(a)
    except sq.IntegrityError:
        flag = 1
        print("\n-------------MESSAGE-----------\n")
        print("Username already exist!")
        print("\n--------------------------------\n")
    finally:
        conn.commit()
        conn.close()
    if flag == 0:
        print("\n-------------MESSAGE-----------\n")
        print("Signed up! Log in now!")
        print("\n--------------------------------\n")

def hashlog(a,b):
    mdhash, dbresult, credentials = [], [], []
    
    mdhash.append(md5_to_hex(md5(a)))
    mdhash.append(md5_to_hex(md5(b)))

    conn1 = sq.connect("prode.db")
    query = "select * from prologde where prouserde = '"+mdhash[0]+"'"
    rs = conn1.execute(query)

    for i in rs:
        dbresult = i

    for k in dbresult:
        credentials.append(k)

    if(len(credentials) == 2):
        if(mdhash[1] == credentials[1]):
            print("\n-------------MESSAGE-----------\n")
            print("             Logged in")
            print("\n--------------------------------\n")
        else:
            print("\n-------------MESSAGE-----------\n")
            print("             Failed")
            print("\n--------------------------------\n")
    else:
        print("\n-------------MESSAGE-----------\n")
        print("             Failed")
        print("\n--------------------------------\n")

if __name__=='__main__':
    while True:
        print("Enter your Choice:")
        print("1) Login")
        print("2) SignUp")
        print("3) Exit")
        ch = int(input())
        
        if ch == 1:
            username = str(input("Enter Your Username "))
            password = str(input("Enter Your Password "))
            hashlog(str.encode(username), str.encode(password))
        elif ch == 2:
            username = str(input("Enter Your Username "))
            password = str(input("Enter Your Password "))
            hashsignup(str.encode(username), str.encode(password))
        elif ch == 3:
            break
        else:
            print("Wrong Choice")
    sys.exit()
    
    
