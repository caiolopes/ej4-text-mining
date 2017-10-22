import sys, json, operator



with open('{}_{}.json'.format(sys.argv[1], sys.argv[2])) as file:
    data = json.loads(file.read())
    newA = dict(sorted(data.items(), key=operator.itemgetter(1), reverse=True)[:100])
    json.dump(newA, open('{}_{}_new.json'.format(sys.argv[1], sys.argv[2]), 'w'))
