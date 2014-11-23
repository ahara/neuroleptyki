import json
import sqlite3


def save_vectors(json_name, vectors):
    with open(json_name, 'w') as f:
        f.write(json.dumps(vectors))

def prepare_vectors(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    vectors = []
    current_patient = None
    current_vector = {}
    i = 0

    for row in c.execute('''
        SELECT
          p.patient_id,
          sex.name,
          p.death_date,
          pre.date,
          pre.international_medicine_name,
          pre.dose
        FROM prescription AS pre
        JOIN patient AS p ON pre.patient=p.id
        JOIN sex ON p.sex = sex.id
        ORDER BY patient, date ASC
        '''):
        if current_patient != row[0] or row[0] is None:
            current_patient = row[0]
            current_vector = {}
            current_vector['sex'] = row[1][0] if row[1] else row[1]
            current_vector['prescriptions'] = []
            current_vector['died'] = bool(row[2])
            current_vector['patient'] = row[0]
            vectors.append(current_vector)
        current_vector['prescriptions'].append((row[3], row[4], row[5]))
        i += 1

    conn.close()
    print 'Sanity check - number of prescriptions in DB', i
    print 'Sanity check - number of prescriptions in JSON', sum([len(v['prescriptions']) for v in vectors])

    return vectors

if __name__ == '__main__':
    db_name = '../test.db'
    vectors = prepare_vectors(db_name)
    #print [v for v in vectors if v['died']][0]
    json_name = 'neuroleptyki_cleared.json'
    save_vectors(json_name, vectors)