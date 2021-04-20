import random
from base64 import b64encode, b64decode
from flask import Flask
from blockchain import blockchain_send, blockchain_print, GAME_INITIALIZE, GAME_START, GAME_END, GAME_COMPLAINT
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
    dict(type=GAME_INITIALIZE, game_id=game_id, encrypted_service_random=encrypted_service_random)
)

player_random_numbers = [
    dict(player_id=1, random_number=5),
    dict(player_id=2, random_number=6),
    dict(player_id=3, random_number=7),
    dict(player_id=4, random_number=8),
    dict(player_id=5, random_number=9)
]

start_block = blockchain_send(
    dict(type=GAME_START, game_id=game_id, player_random_numbers=player_random_numbers)
)

complaint_block = None #blockchain_send(
    #dict(type=GAME_COMPLAINT, game_id=game_id, player_random_number=dict(player_id=3, random_number=7))
#)


if initialization_block and start_block and not complaint_block:
    initialization_block_service_random = initialization_block['content']['encrypted_service_random']

    start_block_hash = start_block['hash']
    start_block_tx_id = start_block['content']['tx_id']
    start_block_player_random_numbers = 0
    for player_random_number in start_block['content']['player_random_numbers']:
        start_block_player_random_numbers += player_random_number['random_number']

    random_number = (
        int.from_bytes(bytes(start_block_hash, 'utf-8'), 'big') +
        int.from_bytes(bytes(start_block_tx_id, 'utf-8'), 'big') +
        decrypt(initialization_block['content']['encrypted_service_random'] + 
        start_block_player_random_numbers)
    ) % 6

    if random_number == 0:
        random_number = 6


    blockchain_send(dict(type=GAME_END, game_id=game_id, random_number=random_number, secret_key=SECRET_KEY))
blockchain_print()