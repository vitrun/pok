import sys

#Let two primes be p = 7 and q = 13. Thus, modulus n = pq = 7 x 13 = 91.
p, q = 7, 13

#Select e = 5, which is a valid choice since there is no number that is common factor of 5 and (p − 1)(q − 1) = 6 × 12 = 72, except for 1.
print('select a valid e so that there is no number that is common factor of e and 72')
e, plain = int(sys.argv[1]), int(sys.argv[2])
n = p * q

if plain >= n:
    exit('number to be encrypted should not be greater than ' + str(n))

#The pair of numbers (n, e) = (91, e) forms the public key and can be made available to anyone whom we wish to be able to send us encrypted messages.
print('public key: ', (n, e))

#Private Key d is the inverse of e modulo (p - 1)(q – 1): ed = 1 mod (p − 1)(q − 1)
d, tmp = 0, (p-1)*(q-1)
for i in range(1, tmp):
    if e * i % tmp == 1:
        d = i

print('private key: ', (n, d))

encrypted = plain**e % n

print('encrypted: ', encrypted)

print('decrypted: ', encrypted**d % n)

