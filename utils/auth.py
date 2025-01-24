import bcrypt

# Hash password
def hash_password(password):
    salt = bcrypt.gensalt()
    # print(salt)
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(hashed_password, password):
    if isinstance(password, str):
        # print(password)
        password = password.encode('utf-8')
        # print(password)
    return bcrypt.checkpw(password, hashed_password)