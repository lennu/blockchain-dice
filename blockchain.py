from flask import Flask, request, jsonify
import json
import hashlib
from uuid import uuid4


GAME_INITIALIZE = 'game_initialize'
GAME_START = 'game_start'
GAME_END = 'game_end'


app = Flask(__name__)


_blockchain = []


def _sha256sum(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _read():
    return _blockchain


def _commit(content):
    content['tx_id'] = str(uuid4())
    blockchain = _read()
    previous_hash = '0'
    try:
        previous_hash = blockchain[-1]['hash']
    except Exception:
        pass
    hash = _sha256sum(str(content))
    block = dict(hash=hash, previous_hash=previous_hash, content=content)
    blockchain.append(block)
    _blockchain = blockchain
    return block


def _is_type_not_allowed(game_id, content_type):
    game_content_type = None
    for block in _read():
        if  block['content']['game_id'] == game_id:
            game_content_type = block['content']['type']

    if content_type != GAME_INITIALIZE and game_content_type == None:
        return True
    elif game_content_type == content_type:
        return True
    else:
        return False


def  _game_transaction(content):
    game_id = content['game_id']
    content_type = content['type']
    if _is_type_not_allowed(game_id=game_id, content_type=content_type):
        print(f'Game {game_id}: already {content_type}')
        return None

    block = _commit(content)
    print(f'Game {game_id}: {content_type}')
    return block


def _run_smart_contracts(content):
    if content['game_id'] and content['type'] in [GAME_INITIALIZE, GAME_START, GAME_END]:
        return _game_transaction(content)
    else:
        return null


def blockchain_send(content):
    return _run_smart_contracts(content)


def blockchain_print():
    print(json.dumps(_read(), indent=2, sort_keys=True))


headers = {'Access-Control-Allow-Origin': '*'}

@app.route('/', methods=['POST'])
def post():
    outcome = _run_smart_contracts(request.json)
    if outcome is not None:
        return (outcome, headers)
    else:
        return ('', 400)

@app.route('/', methods=['GET'])
def get():
    return (jsonify(_read()), headers)

app.run(port=5001, debug=True)