import json
import sqlite3

def save_vectors(json_name, vectors):
    """Save vectors in json file.

    Parameters:
    json_name - name of json file
    vectors   - array containing vectors
    """

    with open(json_name, 'w') as f:
        f.write(json.dumps(vectors))

def get_heart_prescriptions(conn, patient_id):
    """Get cardio prescription array for given patient.

    Parameters:
    conn - database connection object
    patient_id - patient's id in database
    """

    c = conn.cursor()
    c.execute('''
        SELECT
            date,
            international_medicine_name,
            dose
        FROM prescription_heart
        WHERE patient = ?
        ORDER BY date
        ''', [patient_id])
    return c.fetchall()


def prepare_vectors(db_name):
    """Create patient vectors from database.

    Parameters:
    db_name - name of database file
    """

    print "Preparing vectors"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    vectors = []
    current_patient = None
    current_vector = {}
    i = 0

    for row in c.execute('''
        SELECT
          p.id,
          p.patient_id,
          sex.name,
          p.birth_date,
          p.death_date,
          pre.date,
          pre.international_medicine_name,
          pre.dose
        FROM prescription AS pre
        JOIN patient AS p ON pre.patient=p.id
        JOIN sex ON p.sex = sex.id
        ORDER BY patient, date ASC
        '''):
        if current_patient != row[1] or row[1] is None:
            current_patient = row[1]
            current_vector = {}
            current_vector['sex'] = row[2][0] if row[2] else row[2]
            current_vector['prescriptions'] = []
            current_vector['prescriptions_heart'] = get_heart_prescriptions(conn, row[0])
            current_vector['birth'] = row[3]
            current_vector['died'] = row[4]
            current_vector['patient'] = row[1]
            vectors.append(current_vector)
        current_vector['prescriptions'].append((row[5], row[6], row[7]))
        i += 1
        if i % 1000 == 0:
            print i, "iterations done"

    conn.close()
    print 'Sanity check - number of prescriptions in DB', i
    print 'Sanity check - number of prescriptions in JSON', sum([len(v['prescriptions']) for v in vectors])

    return vectors

if __name__ == '__main__':
    db_name = '../nasercowe.db'
    vectors = prepare_vectors(db_name)
    #print [v for v in vectors if v['died']][0]
    json_name = 'test.json'
    save_vectors(json_name, vectors)