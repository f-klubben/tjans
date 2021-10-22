from .message import Message
from .team import Team
from .auction import Auction

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List

LOG_DIR = 'logs'
TIMESTAMP = datetime.now().strftime('%d-%m-%Y')


class MessageLogger:
    LOG_NAME = 'message-log'

    def __init__(self):
        self.path = f'{LOG_DIR}/{self.LOG_NAME}-{TIMESTAMP}.txt'

        if not os.path.isfile(self.path):
            Path(self.path).touch(0o666, exist_ok=True)

    def log_msg(self, msg: Message):
        with open(self.path, 'a') as f:
            f.write(msg.txt + '\n')


class StateLogger:
    LOG_NAME = 'state-log'

    def __init__(self):
        self.path = f'{LOG_DIR}/{self.LOG_NAME}-{TIMESTAMP}.json'

        if not os.path.isfile(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(json.dumps({
                    'teams': [],
                    'auctions': [],
                    'completed_auctions': [],
                    'cur_auction': None
                }))

    def log_state(self, teams: List[Team], auctions: List[Auction],
                  completed_auctions: List[Auction], cur_auction: Auction):
        log = {
            'teams': [x.to_json() for x in teams],
            'auctions': [x.to_json() for x in auctions],
            'completed_auctions': [x.to_json() for x in completed_auctions],
            'cur_auction': cur_auction.to_json() if cur_auction else {}
        }

        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(log, indent=4, ensure_ascii=False))

    def load_state(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())

        teams = [Team.from_json(x) for x in data['teams']]
        auctions = [Auction.from_json(x) for x in data['auctions']]
        completed_auctions = [Auction.from_json(x) for x in data['completed_auctions']]
        cur_auction = Auction.from_json(data['cur_auction'])

        return teams, auctions, completed_auctions, cur_auction

    def is_state_log_present(self) -> bool:
        with open(self.path, 'r') as f:
            data = json.loads(f.read())

        # allow completed auctions to be empty
        return all(bool(data[key]) for key in ['teams', 'auctions', 'cur_auction']) and 'completed_auctions' in data.keys()