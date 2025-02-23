#  TEST

from cryptography.fernet import Fernet
from django.conf import settings
import base64
code_bytes = settings.SECRET_KEY.encode("utf-8")
key = base64.urlsafe_b64encode(code_bytes.ljust(32)[:32])
cipher_suite = Fernet(key)
def encrypt_email(email):
    encrypted_email = cipher_suite.encrypt(email.encode())
    return encrypted_email.decode()
def decrypt_email(encrypted_email):
    decrypted_email = cipher_suite.decrypt(encrypted_email.encode())
    return decrypted_email.decode()