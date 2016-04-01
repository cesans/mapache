class PartyArray:

    def __init__(self, context_name = ''):
        self.context_name = context_name
        self.parties = {}

    def __iter__(self):
        self.current = -1
        return self

    def __getitem__(self, key):
        return self.parties[key.upper()]

    def __delitem__(self, key):
        del self.parties[key]

    def __setitem__(self, key, value):
        self.parties[key] = value

    def __next__(self):
        if self.current == len(self.parties)-1:
            raise StopIteration
        else:
            self.current += 1
            return self.parties[self.current]

    def add(self, party):
        self.parties[party.name.upper()] = party

    def keys(self):
        return self.parties.keys()