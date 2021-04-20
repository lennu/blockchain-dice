import json
import hashlib
from uuid import uuid4


GAME_INITIALIZE = 'game_initialize'
GAME_START = 'game_start'
GAME_END = 'game_end'


_blockchain_file = 'blockchain.json'


def _sha256sum(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _read():
     with open(_blockchain_file, 'r') as json_file:
         return json.load(json_file)


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
    with open(_blockchain_file, 'w+') as json_file:
        json.dump(blockchain, json_file)
    return block


def _initialize():
    try:
        _read()
    except Exception:
        with open(_blockchain_file, 'w+') as json_file:
            json.dump([], json_file)


def  _new_transaction(content):
    game_id = content['game_id']
    content_type = content['type']
    for block in _read():
        if  block['content']['game_id'] == game_id and block['content']['type'] == content_type:
            print(f'Game {game_id}: already {content_type} ({block["hash"]})')
            return block

    block = _commit(content)
    print(f'Game {game_id}: {content_type} ({block["hash"]})')
    return block

def _run_smart_contracts(content):
    if content['game_id'] and content['type']:
        return _new_transaction(content)
    else:
        return null

def blockchain_send(content):
    return _run_smart_contracts(content)

def blockchain_print():
    print(json.dumps(_read(), indent=2, sort_keys=True))

_initialize()