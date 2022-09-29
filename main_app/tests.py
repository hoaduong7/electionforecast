from django.test import TestCase
from django.test import Client
import timeit

print("Blake2S")
print (timeit.repeat(
"""
import hashlib
for line in urls:
#    h = hashlib.md5(line).hexdigest()
#    h = hashlib.sha1(line).hexdigest()
#    h = hashlib.sha256(line).hexdigest()
#    h = hashlib.sha512(line).hexdigest()
#    h = hashlib.blake2b(line).hexdigest()
    h = hashlib.blake2s(line).hexdigest()
"""
,
"""
urls = [l.encode('utf8') for l in open('urls.txt', 'r').readlines()]
""",
repeat=3, number=1000))
