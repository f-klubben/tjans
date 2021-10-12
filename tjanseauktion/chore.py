import json


class Chore:

    def __init__(self, desc: str, day: str, time: str):
        self.desc = desc
        self.day = day
        self.time = time

    def __str__(self) -> str:
        return f'{self.desc} - {self.day} at {self.time}'

    def __eq__(self, other):
        if not other:
            return False
        return self.desc == other.desc and self.day == other.day and self.time == other.time

    @classmethod
    def load_chores(cls, path: str = 'data/chores.json') -> list:
        """
        Load all chores from ./data/chores.json and return them as a list of Chore objects
        """
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
