from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
from Crypto import Random

def rsa_encrypt(message):
    with open('server.txt') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(message.encode()))
        return cipher_text


def rsa_decrypt(message):
    with open('server-key.txt') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        byte_msg = base64.b64decode(message)
        random_generator = Random.new().read
        return cipher.decrypt(byte_msg, random_generator)


encrypt_message = rsa_encrypt('1231231231')
print(encrypt_message)

decrypt_message = rsa_decrypt(encrypt_message)
print(decrypt_message)