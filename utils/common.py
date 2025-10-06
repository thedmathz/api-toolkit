import re
import random
import string

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choices(characters, k=length))

def smart_title(s):
    return ' '.join([word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper() for word in s.split()])

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^a-zA-Z0-9]", password):
        return False
    return True