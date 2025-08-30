from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from django.conf import settings
import base64
import hashlib
from cryptography.fernet import Fernet

from.models import User,UserKeyPair

key_hash = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
fernet_key = base64.urlsafe_b64encode(key_hash)
fernet = Fernet(fernet_key)

def encrypt_key(key_data: bytes) -> str:
    return fernet.encrypt(key_data).decode()

def decrypt_key(encrypted_data: str) -> bytes:
    return fernet.decrypt(encrypted_data.encode())

def generate_keys(key_size=2048): #Generates RSA
    key = RSA.generate(key_size)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def sign_message(private_key_bytes: bytes, message: bytes) -> bytes: #Digitally Sign Documents 
    private_key = RSA.import_key(private_key_bytes)
    h = SHA256.new(message)
    signature = pkcs1_15.new(private_key).sign(h)
    return signature

def verify_signature(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
    # Verify the documents
    public_key = RSA.import_key(public_key_bytes)
    h = SHA256.new(message)
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

def create_or_update_user_keys(user: User):
    
    UserKeyPair.objects.filter(user=user).delete()

    private_key_bytes, public_key_bytes = generate_keys()
    encrypted_private_key = encrypt_key(private_key_bytes)

    UserKeyPair.objects.create(
        user=user,
        public_key=public_key_bytes.decode('utf-8'),
        private_key_encrypted=encrypted_private_key
    )