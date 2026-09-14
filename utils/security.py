# -*- coding: utf-8 -*-
import hashlib
import os
import secrets
import re

def generate_salt() -> str:
    return secrets.token_hex(16)

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = generate_salt()
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return key.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)

def sanitize_filename(filename: str) -> str:
    name = os.path.basename(filename)
    name = re.sub(r'[^a-zA-Z0-9_.-]', '_', name)
    return name

def format_cnpj(cnpj: str) -> str:
    nums = re.sub(r'\D', '', str(cnpj or ''))
    if len(nums) == 14:
        return f'{nums[:2]}.{nums[2:5]}.{nums[5:8]}/{nums[8:12]}-{nums[12:]}'
    return cnpj

def format_phone(phone: str) -> str:
    nums = re.sub(r'\D', '', str(phone or ''))
    if len(nums) == 11:
        return f'({nums[:2]}) {nums[2:7]}-{nums[7:]}'
    elif len(nums) == 10:
        return f'({nums[:2]}) {nums[2:6]}-{nums[6:]}'
    return phone or ''

def mask_email(email: str) -> str:
    if '@' not in str(email):
        return email
    user, domain = email.split('@', 1)
    if len(user) <= 2:
        masked_user = user[0] + '*'
    else:
        masked_user = user[:2] + '*' * (len(user) - 3) + user[-1]
    return f'{masked_user}@{domain}'
