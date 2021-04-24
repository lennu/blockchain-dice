import random
from flask import Flask, request, render_template, jsonify
import requests


GAME_INITIALIZE = 'game_initialize'
GAME_START = 'game_start'
GAME_END = 'game_end'
BLOCKCHAIN_URL = 'http://localhost:5001'


app = Flask(__name__)


PUBLIC_KEY = 12345
SECRET_KEY = 12345


def _encrypt(number):
    return number * PUBLIC_KEY


def _decrypt(number):
    return int(number / SECRET_KEY)


_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, DELETE',
    'Access-Control-Allow-Headers': 'Content-Type',
}


ok = ('',  200, _headers)
bad_request = ('',  400, _headers)


def _handle_response(response):
    if response.status_code >= 400:
        return bad_request
    return ok


def _get_next_game_id():
    game_id = 1
    blockchain = requests.get(url=BLOCKCHAIN_URL).json()
    for block in blockchain:
        if block['content']['type'] == GAME_INITIALIZE:
            game_id = block['content']['game_id'] + 1
    return game_id


def _get_game_blocks(game_id):
    initialization_block = None
    start_block = None

    blockchain = requests.get(url=BLOCKCHAIN_URL).json()
    for block in blockchain:
        if block['content']['game_id'] == game_id:
            if block['content']['type'] == GAME_INITIALIZE:
                initialization_block = block
            if block['content']['type'] == GAME_START:
                start_block = block

    return (initialization_block, start_block)


def _calculate_random_number(initialization_block, start_block):
    initialization_block_encrypted_service_random = initialization_block['content']['encrypted_service_random']
    start_block_hash = start_block['hash']
    start_block_tx_id = start_block['content']['tx_id']
    start_block_player_random_numbers = 0
    for player_random_number in start_block['content']['player_random_numbers']:
        start_block_player_random_numbers += player_random_number['random_number']

    random_number = (
        int.from_bytes(bytes(start_block_hash, 'utf-8'), 'big') +
        int.from_bytes(bytes(start_block_tx_id, 'utf-8'), 'big') +
        _decrypt(initialization_block_encrypted_service_random) +
        start_block_player_random_numbers
    ) % 6

    if random_number == 0:
        random_number = 6

    return random_number


@app.route('/', methods=['GET'])
def ui():
    return render_template('./index.html')


@app.route('/game-initialize', methods=['POST', 'OPTIONS'])
def game_initialize():
    if request.method == 'OPTIONS':
        return ok

    game_id = _get_next_game_id()
    encrypted_service_random = _encrypt(random.randrange(0, 100))

    response = requests.post(
        url=BLOCKCHAIN_URL,
        json=dict(type=GAME_INITIALIZE, game_id=game_id, encrypted_service_random=encrypted_service_random)
    )
    return _handle_response(response=response)


@app.route('/game-start', methods=['POST', 'OPTIONS'])
def game_start():
    if request.method == 'OPTIONS':
        return ok

    game_id = request.json['game_id']
    player_random_numbers = request.json['player_random_numbers']

    response = requests.post(
        url=BLOCKCHAIN_URL,
        json=dict(type=GAME_START, game_id=game_id, player_random_numbers=player_random_numbers)
    )

    return _handle_response(response=response)


@app.route('/game-end', methods=['POST', 'OPTIONS'])
def game_end():
    if request.method == 'OPTIONS':
        return ok

    game_id = request.json['game_id']
    game_details = request.json['game_details']

    initialization_block, start_block = _get_game_blocks(game_id)

    if initialization_block is None or start_block is None:
        return bad_request

    random_number = _calculate_random_number(initialization_block=initialization_block, start_block=start_block)

    response = requests.post(
        url=BLOCKCHAIN_URL,
        json=dict(type=GAME_END, game_id=game_id, random_number=random_number, secret_key=SECRET_KEY, game_details=game_details)
    )

    return _handle_response(response=response)


app.run(port=5000, debug=True)