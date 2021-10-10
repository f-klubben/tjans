import json


class Chore:

    def __init__(self, desc: str, day: str, time: str):
        self.desc = desc
        self.day = day
        self.time = time

    def __str__(self) -> str:
        return f'{self.desc} - {self.day} at {self.time}'

    @classmethod
    def load_chores(cls) -> list:
        """
        Load all chores from ./data/chores.json and return them as a list of Chore objects
        """
        path = 'data/chores.json'

        with open(path, 'r') as f:
            data = json.loads(f.read())

        return [cls.from_json(row) for row in data]

    @classmethod
    def from_json(cls, row: dict):
        """
        Convert a JSON row to a Chore object
        """
        return Chore(row['desc'], row['day'], row['time'])

    def to_json(self):
        return {
            'desc': self.desc,
            'day': self.day,
            'time': self.time
        }
