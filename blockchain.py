from flask import Flask, request, jsonify
import json
import hashlib
from uuid import uuid4
import sys
import requests


GAME_INITIALIZE = 'game_initialize'
GAME_START = 'game_start'
GAME_END = 'game_end'
REGISTER = 'register'


app = Flask(__name__)


_blockchain = []


node_port = None
register_url = None
if len(sys.argv) == 1:
    exit()
elif len(sys.argv) == 2:
    node_port = sys.argv[1]
elif len(sys.argv) == 3:
    node_port = sys.argv[1]
    register_url = sys.argv[2]


def _sha256sum(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _overwrite(data):
    _blockchain.clear()
    for block in data:
        _blockchain.append(block)


def _get_nodes():
    nodes = []
    for block in _blockchain:
        if block['content']['type'] == REGISTER:
            nodes.append(block['content']['node_url'])
    return nodes


def _synchronize_nodes():
    nodes = _get_nodes()
    for node in nodes:
        if node_port not in node:
            requests.post(
                url=f'{node}/synchronize',
                json=_blockchain
            )


def _commit(content):
    content['tx_id'] = str(uuid4())
    previous_hash = '0'
    try:
        previous_hash = _blockchain[-1]['hash']
    except Exception:
        pass
    hash = _sha256sum(str(content))
    block = dict(hash=hash, previous_hash=previous_hash, content=content)
    _blockchain.append(block)
    return block


def _register(content):
    nodes = _get_nodes()
    if content["node_url"] in nodes:
        print(f'Node {content["node_url"]} already registered')
        return None
    block = _commit(content)
    print(f'Node {content["node_url"]} registered')


def _is_type_not_allowed(game_id, content_type):
    game_content_type = None
    for block in _blockchain:
        if  block['content'].get('game_id') == game_id:
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
    if content.get('game_id') and content['type'] in [GAME_INITIALIZE, GAME_START, GAME_END]:
        return _game_transaction(content)
    else:
        return None


headers = {'Access-Control-Allow-Origin': '*'}


@app.route('/', methods=['POST'])
def post():
    outcome = _run_smart_contracts(request.json)
    if outcome is not None:
        _synchronize_nodes()
        return ('', 200)
    else:
        return ('', 400)


@app.route('/register', methods=['POST'])
def register():
    _register(request.json)
    return (jsonify(_blockchain), 200)


@app.route('/synchronize', methods=['POST'])
def synchronize():
    _overwrite(request.json)
    return ('', 200)


@app.route('/', methods=['GET'])
def get():
    return (jsonify(_blockchain), headers)


register_content = dict(type=REGISTER, node_url=f'http://localhost:{node_port}')
if register_url is not None:
    response = requests.post(
        url=f'{register_url}/register',
        json=register_content
    )
    _overwrite(response.json())
    _synchronize_nodes()
else:
    _register(register_content)


app.run(port=node_port, debug=True)
