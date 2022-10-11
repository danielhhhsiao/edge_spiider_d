from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from datetime import datetime
import time
import argparse

def uncrypto(input_F,output_F,privateFile="private.pem"):
    # 讀取 RSA 私鑰
    privateKey = RSA.importKey(open(privateFile).read())

    # 從檔案讀取加密資料
    with open(input_F, "rb") as f:
        encSessionKey = f.read(privateKey.size_in_bytes())
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read(-1)
    print("Input file:",input_F,"Size:",len(ciphertext)+len(nonce)+len(tag))

    # 以 RSA 金鑰解密 Session 金鑰
    cipherRSA = PKCS1_OAEP.new(privateKey)
    sessionKey = cipherRSA.decrypt(encSessionKey)

    # 以 AES Session 金鑰解密資料
    cipherAES = AES.new(sessionKey, AES.MODE_EAX, nonce)
    data = cipherAES.decrypt_and_verify(ciphertext, tag)

    # 輸出解密後的資料
    with open(output_F, "wb") as f:
        f.write(data)
    print("Output file:",output_F,"Size:",len(data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input",type=str,help="Input file path")
    parser.add_argument("output",type=str,help="Output file path")
    args = parser.parse_args()
            
    uncrypto(args.input,args.output)
        
