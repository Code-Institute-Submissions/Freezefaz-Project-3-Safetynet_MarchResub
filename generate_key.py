import os
import binascii

# to create a secret key
print(binascii.hexlify(os.urandom(24)))