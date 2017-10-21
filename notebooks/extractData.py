import re

def data(text):
    p = re.compile('\d\d\sde\s[a-zA-Z]+\s\d\d\d\d')
    for line in text.splitlines():
        print('ok')
        if p.search(line) is not None:
            return line
    return 'Not found'

from glob import glob
from os import path

DIR = './data'
def document_iterator(DIR):
    for index, file in enumerate(glob(path.join(DIR, '*.txt)'))):
        yield open (file, 'r', enconding='cp1252').read()
        if index >= 9:
            break

for text in document_iterator(DIR):
    print(data(text))
