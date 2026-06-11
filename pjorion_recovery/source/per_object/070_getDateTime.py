# recovered via pycdc

if self.hasLicense():
    data = self.getData()
    return datetime(int(data[1].split('.')[2]), int(data[1].split('.')[1]), int(data[1].split('.')[0]))
