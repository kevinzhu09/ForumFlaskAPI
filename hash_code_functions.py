# External modules: hashlib handles hashing the password. os handles random number generation.
import hashlib

from os import urandom

from config.APIConfig import SALT_LENGTH


def get_hash_code(password):
    salt = urandom(SALT_LENGTH)
    key = calculate_hashed_value(password, salt)

    hash_code = salt + key
    return hash_code


def verify_hash_code(password, hash_code):
    salt = hash_code[:SALT_LENGTH]
    key = hash_code[SALT_LENGTH:]

    new_key = calculate_hashed_value(password, salt)

    return new_key == key


# Helper function to calculate the hashed value from a specified algorithm.
def calculate_hashed_value(password, salt):
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
    return key


# Test to make sure the hash functions are working properly (debugging purposes)
def hash_test():
    password = 'PassWord@~'
    hash_code = get_hash_code(password)
    print(verify_hash_code(password, hash_code))
    print(verify_hash_code('john', hash_code))
    print(type(hash_code))
    print(hash_code)


if __name__ == '__main__':
    hash_test()
