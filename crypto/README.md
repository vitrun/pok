# Crypto Algorithms
## RSA
In RSA, this maximum value (call it max) is obtained by multiplying two random prime numbers.
The public and private keys are two specially chosen numbers that are greater than zero and less than the maximum value, call them pub and priv.
To encrypt a number you multiply it by itself pub times, making sure to wrap around when you hit the maximum.
To decrypt a message, you multiply it by itself priv times and you get back to the original number.

As long as you know the two prime numbers, you can compute a corresponding private key priv from this public key.
This is how *factoring* relates to breaking RSA — factoring the maximum number into its component primes
allows you to compute someone's private key from the public key and decrypt their private messages.

## Diffie-Hellman
Diffie-Hellman is an algorithm used to establish a shared secret between two parties. It is primarily used as a method of exchanging cryptography keys for use in symmetric encryption algorithms like AES.

The algorithm in itself is very simple. Let's assume that Alice wants to establish a shared secret with Bob.

* Alice and Bob agree on a prime number, p, and a base, g, in advance. For our example, let's assume that p=23 and g=5.
* Alice chooses a secret integer a whose value is 6 and computes A = g^a mod p. In this example, A has the value of 8.
* Bob chooses a secret integer b whose value is 15 and computes B = g^b mod p. In this example, B has the value of 19.
* Alice sends A to Bob and Bob sends B to Alice.
* To obtain the shared secret, Alice computes s = B^a mod p. In this example, Alice obtains the value of s=2
* To obtain the shared secret, Bob computes s = A^b mod p. In this example, Bob obtains the value of s=2.

The algorithm is secure because the values of a and b, which are required to derive s are not transmitted across the wire at all.

*Discrete logarithm* problem is used (the g^a mod p business) to ensure security.

## Trapdoor Function
A trapdoor function is a function that is easy to compute in one direction, yet difficult to compute in the opposite direction (finding its inverse) without special information.
Both factoring and discrete logarithm are trapdoors:

* Factoring: given N=pq,p<q,p≈q, find p,q.
* Discrete logarithm: Given p,g,g^x mod p, find x.

Factoring is not the hardest problem on a bit for bit basis. Specialized algorithms like the Quadratic Sieve and the General Number Field Sieve were created to tackle the problem of prime factorization and have been moderately successful.
These factoring algorithms get more efficient as the size of the numbers being factored get larger. The gap between the difficulty of factoring large numbers and multiplying large numbers is shrinking as the number (i.e. the key's bit length) gets larger. As the resources available to decrypt numbers increase, the size of the keys need to grow even faster.

Interestingly, the two problems are related. The general number field sieve, which is generally thought of as a factoring algorithm, is also very useful for solving discrete logs.

## Elliptic Curve
Elliptic curve serves as a better trapdoor function.

An elliptic curve is the set of points that satisfy a specific mathematical equation. The equation for an elliptic curve looks something like this:

y2 = x3 + ax + b

Let's imagine this curve as the setting for a bizarre game of billiards. Take any two points on the curve and draw a line through them, it will intersect the curve at exactly one more place. In this game of billiards, you take a ball at point A, shoot it towards point B. When it hits the curve, the ball bounces either straight up (if it's below the x-axis) or straight down (if it's above the x-axis) to the other side of the curve.
![Elliptic curve](img/elliptic_curve.gif)

We can call this billiards move on two points "dot." Any two points on a curve can be dotted together to get a new point.

It turns out that if you have two points, an initial point "dotted" with itself n times to arrive at a final point, finding out n when you only know the final point and the first point is hard.

## Elliptic Curve Diffie-Hellman

While DH uses a multiplicative group of integers modulo a prime p, ECDH uses a multiplicative group of points on an elliptic curve:
* Alice and Bob agree on an elliptic curve E over a Field 𝔽q and a bsepoint P∈E/𝔽q.
* Alice generates a (random) secret kA and computes PA=kAP.
* Bob generates a (random) secret kB and computes PB=kBP.
* Alice and Bob exchange PA and PB.
* Alice and Bob compute PAB=kaPB=kbPA.

## REF
* https://blog.cloudflare.com/a-relatively-easy-to-understand-primer-on-elliptic-curve-cryptography/
* https://crypto.stanford.edu/pbc/notes/crypto/factoring.html
* https://en.wikipedia.org/wiki/Trapdoor_function
* https://math.stackexchange.com/questions/317898/does-the-difficulty-of-discrete-logarithm-depend-on-the-difficulty-of-integer-fa
* https://crypto.stackexchange.com/questions/29906/how-does-diffie-hellman-differ-from-elliptic-curve-diffie-hellman
