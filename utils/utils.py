import hashlib


def hash_password(password):
    # Hash password
    hash_pass = hashlib.sha512(password.encode("utf-8")).hexdigest()
    return hash_pass
