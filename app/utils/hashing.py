
import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=bcrypt.gensalt())
    return hashed_password