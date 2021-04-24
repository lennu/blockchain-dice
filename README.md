# Blockchain Dice

This is a prototype of a blockchain gambling software where players try to guess the results of a virtual dice roll.

Everything is stored in memory so everytime the software is started it starts with empty blockchain.

There are three type of events:

### game_initialize

In this step game service chooses a game id and encrypts a random number and sends them to the blockchain.

### game_start

In this step players participate to the game by sending random numbers they have chosen to game service which forwards them to the blockchain.

### game_end

In this step the dice is rolled by revealing the secret key of the game service and calculating the random number from certain values within the blockchain and publishing the result eventually to the blockchain.

## Requirements

- [Python 3](https://www.python.org/)
- [flask](https://flask.palletsprojects.com/en/1.1.x/installation/#installation)
- [requests](https://docs.python-requests.org/en/master/user/install/#install)

## Running

In a shell:
```
python blockchain.py
```

And in another shell:
```
python game_service.py
```

The user interface can be found from http://localhost:5000.
