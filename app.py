import random
from base64 import b64encode, b64decode
from flask import Flask
from blockchain import blockchain_send, blockchain_print, GAME_INITIALIZE, GAME_START, GAME_END
import hashlib

app = Flask(__name__)

PUBLIC_KEY = 12345
SECRET_KEY = 12345

def encrypt(number):
    return number * PUBLIC_KEY

def decrypt(number):
    return int(number / SECRET_KEY)

game_id = 1
encrypted_service_random = encrypt(random.randrange(0, 100))

initialization_block = blockchain_send(
    dict(type=GAME_INITIALIZE, game_id=str(game_id), encrypted_service_random=encrypted_service_random)
)
start_block = blockchain_send(
    dict(type=GAME_START, game_id=str(game_id), player_random_numbers=[])
)

start_block_hash = start_block['hash']
start_block_tx_id = start_block['content']['tx_id']
initialization_block_service_random = initialization_block['content']['encrypted_service_random']

random_number = (
    int.from_bytes(bytes(start_block_hash, 'utf-8'), 'big') +
    int.from_bytes(bytes(start_block_tx_id, 'utf-8'), 'big') +
    decrypt(initialization_block['content']['encrypted_service_random'])
) % 6


blockchain_send(dict(type=GAME_END, game_id=str(game_id), random_number=random_number, secret_key=SECRET_KEY))
blockchain_print()