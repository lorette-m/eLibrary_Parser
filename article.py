class Article:
    def __init__(self, number, name):
        self.number = number
        self.name = name

    def write_down(self):
        return f"{self.number} {self.name}"