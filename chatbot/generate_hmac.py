import hmac
import hashlib

def create_signature_variants(api_key, api_secret, data="all"):
    # Вариант 1: простой HMAC-SHA256 в шестнадцатеричном формате
    signature1 = hmac.new(
        api_secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Вариант 2: простой SHA256 хеш от комбинации ключа и данных
    signature2 = hashlib.sha256(
        (api_key + data).encode('utf-8')
    ).hexdigest()
    
    # Вариант 3: SHA256 хеш от комбинации секрета и данных
    signature3 = hashlib.sha256(
        (api_secret + data).encode('utf-8')
    ).hexdigest()
    
    # Вариант 4: MD5 (если используется более простой алгоритм)
    signature4 = hashlib.md5(
        (api_secret + data).encode('utf-8')
    ).hexdigest()
    
    return {
        "hmac_sha256_hex": signature1,
        "sha256_key_data": signature2,
        "sha256_secret_data": signature3,
        "md5_secret_data": signature4
    }

api_key = "OQzfQ1c1LQT4PGA0Qjq4rMu4CgP4gwXu"
api_secret = "2LJe_Vw2mZ29vAdJMuqxL1Fd9L3qpFFqvCDheH8-WZc"

variants = create_signature_variants(api_key, api_secret)
for name, signature in variants.items():
    print(f"{name}: {signature}")