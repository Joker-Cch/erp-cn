try:
    from Crypto.Cipher import AES
    from Crypto import Random
except:
    from Cryptodome.Cipher import AES
    from Cryptodome import Random

from binascii import b2a_hex, a2b_hex
import rsa
from random import randint
from libs.Singleton import Singleton

@Singleton
class Encrypt:
    def config(self, key, ase=True):
        self.ase=True
        self.key = key
    
    def encode(self, key, content):
        if self.ase:
            return self.aseencrypt(key[:16], key[16:], content)

    def decode(self, content):
        if self.ase:
            key, content = content[:16], a2b_hex(content[16:])
            iv, content = content[-16:], content[:-16]
            return self.asedecrypt( key, iv, content)
            
    def genSecret(self):
        if self.ase:
            key = self.key[randint(0,len(self.key)-1)] if isinstance(self.key, list) else self.key
            iv = b2a_hex(Random.new().read(AES.block_size)).decode("utf8")
            return key+iv
    
    def aseencrypt(self, key, iv, content):
        
        iv = a2b_hex(iv.encode('utf8'))
        cipher = AES.new(key.encode("utf8"), AES.MODE_CFB, iv)
        key = self.resetkey(key, False)
        return key + b2a_hex(cipher.encrypt(content.encode("utf8"))+iv).decode('utf8')

    def asedecrypt(self, key, iv, content):
        key = self.resetkey(key, True)
        cipher = AES.new(key.encode("utf8"), AES.MODE_CFB, iv)
        return cipher.decrypt(content).decode()

    def resetkey(self, key, reset = True):
        if not reset:
            key = key[0]+key[1:6].replace(key[0]," ")+key[6:10]+key[10:].replace(key[7], ".")
        else:
            key = key[0]+key[1:6].replace(" ", key[0])+key[6:10]+key[10:].replace(".", key[7])
        return key