import os
import re 

from unicodedata import normalize

def normalized(text):
    try:
        return normalize('NFKD', text).encode('ASCII','ignore').decode('ASCII')
    except:
        pass
    return text


def read_files():
    path = '../data'
    results = []
    missing = {
        'author': 0,
        'process': 0,
        'lawyers': 0,
    }

    for filename in os.listdir(path)[:10]:
        with open('./{}/{}'.format(path, filename), encoding="cp1252") as f:
            text = f.read()
            text = normalized(text)
            print(filename)

            author = get_author(text)
            process_num = get_process_num(text)
            lawyers = get_lawyer(text)

            results.append({
                filename: {
                    'process': process_num, 
                    'author': author,
                    'lawyers': lawyers,
                }
            })

            if not author:
                missing['author'] += 1
            if not process_num:
                missing['process'] += 1
            if not lawyers:
                missing['lawyers'] += 1
            
            if pos%500 == 0:
                print(pos, missing)

    # print('\n\n\n', results)
    print('Missing', missing)

def get_process_num(content):
    process_num_matches = re.findall(r"proc(?:esso|.)(?:[^\d]{0,15})(\d|-|\.|\s?\/\s?)*", content, re.IGNORECASE)
    for match in process_num_matches:
        if match:
            return match
    return None
    
def get_author(content):
    author_matches = re.findall(r"(?:(?:a|A)utora?|AUTORA?|(?:R|r)equerente|REQUERENTE|(?:(?:P|p)romovente|PROMOVENTE)\(?(?:S|s)?\)?|(?:D|d)emandante|DEMANDANTE)(?:[^A-Z])*([A-Z][^\n]*)|(?:(?:V|v)istos?|VISTOS?)(?:[^A-Z]*)([A-Z\s][^a-z]*)", content)
    for match in author_matches:
        for author in match:
            if author:
                return re.sub('[^\w\s]','',author)
    return None

def get_lawyer(content):
    lawyer_matches = re.findall(r"(?:Adv(?:ogado)?(?:\(a\))?|Procurador)\W[^A-Z]*([A-Z][^\n(-]*)", content)
    lawyers = []

    for lawyer in lawyer_matches:
        if lawyer and len(lawyer.split()) <= 5:
            lawyers.append(lawyer.strip())
        
    return lawyers if lawyers else None

if __name__ == '__main__':
    read_files()