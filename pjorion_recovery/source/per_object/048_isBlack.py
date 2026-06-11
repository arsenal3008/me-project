# recovered via pycdc

for id in self.black_list:
    if self.campHash(self.getID(), self.getHash(id)):
        return True
    for h in self.black_hard:
        if self.campHash(self.getID(), self.getHash(id)):
            return True
        return None
