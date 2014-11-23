import json
import datetime
from collections import Counter


def get_vectors(path='../db2vectors/neuroleptyki_cleared.json'):
    with open(path, 'rb') as f:
        return json.load(f)

def date_diff(date1, date2):
    d1 = datetime.datetime.strptime(date1, '%Y/%m/%d')
    d2 =  datetime.datetime.strptime(date2, '%Y/%m/%d')
    delta = d2-d1
    return delta.days

def prescription_chains(prescriptions):
    chains = []
    c = []
    last_prescription = None
    for p in prescriptions:
        if last_prescription and date_diff(last_prescription[0], p[0]) > 90:
            # Starting new chain
            chains.append(c)
            c = []
        c.append(p)
    chains.append(c)
    return chains

def data_to_chains(data):
    chains = []
    for d in data:
        chains += prescription_chains(d['prescriptions'])
    return chains

def analyse_medicine_sequences(chains):
    counter = Counter()
    for c in chains:
        medicines = [p[1] for p in c]
        key = '_'.join(medicines)
        counter[key] += 1
    return counter

def print_stat(counter, n=10, path=None):
    lines = []
    lines.append('Number of sequences %d' % len(counter.keys()))
    for k, v in counter.most_common(n) if n else counter.most_common():
        lines.append('%s: %s' % (k.replace('_', ' '), v))
    output = '\n'.join(lines)
    if path:
        with open(path, 'w') as f:
            f.writelines(output)
    else:
        print output


if __name__ == '__main__':
    vectors = get_vectors()
    print 'Sanity check - number of vectors', len(vectors)
    print 'Sanity check - number of prescriptions', sum([len(v['prescriptions']) for v in vectors])
    chains = data_to_chains(vectors)
    counter = analyse_medicine_sequences(chains)
    print_stat(counter, 0, 'top_sequences.txt')
    print 'Sanity check - number of prescriptions', sum([v for _, v in counter.items()])
    print 'Finished'
    