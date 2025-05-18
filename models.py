class Article:
    def __init__(self, number, name):
        self.number = number
        self.name = name

    def write_down(self):
        line = self.number + " " + self.name
        return line