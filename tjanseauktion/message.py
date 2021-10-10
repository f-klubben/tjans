

class Message:

    def __init__(self, txt: str, attr: int = 0):
        self.txt = txt
        self.attr = attr

    def __eq__(self, other):
        if not other:
            return False
        return self.txt == other.txt
