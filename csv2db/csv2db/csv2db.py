import csv
import re
import sqlite3

def read_data_from_file(file_path):
    records = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        # Skip headers
        next(reader, None)
        for row in reader:
            records.append(row)
    return records

def create_tables(db_name):
    # Create connection to DB
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('CREATE TABLE sex (id INTEGER PRIMARY KEY, name TEXT)')
    c.execute('''CREATE TABLE patient (
                    id INTEGER PRIMARY KEY,
                    patient_id TEXT,
                    birth_date TEXT,
                    death_date TEXT,
                    sex INTEGER,
                    FOREIGN KEY(sex) REFERENCES sex(id))'''
                    )
    c.execute('''CREATE TABLE prescription (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    patient INT,
                    international_medicine_name TEXT,
                    polish_medicine_name TEXT,
                    dose TEXT,
                    FOREIGN KEY(patient) REFERENCES patient(id))''')

    conn.commit()
    conn.close()

def normalize_date(date):
    pattern = re.compile(r'(\d+)-(\d+)-(\d+)')
    match = re.search(pattern, date)
    if match:
        l = [d if len(d) > 1 else '0'+d for d in match.groups()]
        return '/'.join([l[2], l[0], l[1]])
    else:
        pattern = re.compile(r'(\d+)-(\d+)-(\d+)')
        match = re.search(pattern, date)
        if match:
            return date.replace('-', '/')
        raise Exception('Cannot convert date: %s', date)

def normalizer(data, is_text=True):
    if data is None or data == 'brak danych' or len(data) == 0:
        return 'NULL'
    else:
        return "'%s'" % data if is_text else data

def get_with_add_sex(conn, sex_name):
    # Find sex
    c = conn.cursor()
    norm_sex = normalizer(sex_name)
    s = next(c.execute('SELECT id FROM sex WHERE name = %s' % norm_sex), None)

    if s is None and norm_sex != 'NULL':
        c.execute('INSERT INTO sex (name) VALUES (%s)' % norm_sex)
        #conn.commit()
        s = next(c.execute('SELECT id FROM sex WHERE name = %s' % norm_sex), None)
    return s[0] if s is not None else None

def get_with_add_patient(conn, patient_id, birth_date, death_date, sex):
    # Find patient
    c = conn.cursor()
    norm_patient_id = normalizer(patient_id)
    s = next(c.execute('SELECT id FROM patient WHERE patient_id = %s' % norm_patient_id), None)

    if s is None and norm_patient_id != 'NULL':
        norm_birth = normalizer(birth_date)
        norm_death = normalizer(death_date)
        norm_sex = normalizer(sex) if sex is None else sex
        c.execute('INSERT INTO patient (patient_id, birth_date, death_date, sex) VALUES (%s, %s, %s, %s)' % 
                  (norm_patient_id, norm_birth, norm_death, norm_sex))
        #conn.commit()
        s = next(c.execute('SELECT id FROM patient WHERE patient_id = %s' % norm_patient_id), None)
    return s[0] if s is not None else None

def add_prescription(conn, date, patient, international_medicine_name, polish_medicine_name, dose):
    c = conn.cursor()
    norm_date = normalizer(normalize_date(date))
    norm_patient = normalizer(patient) if patient is None else patient
    norm_inter_medicine = normalizer(international_medicine_name)
    norm_polish_medicine = normalizer(polish_medicine_name)
    norm_dose = normalizer(dose)
    
    c.execute('INSERT INTO prescription (date, patient, international_medicine_name, polish_medicine_name, dose) VALUES (%s, %s, %s, %s, %s)' %
              (norm_date, norm_patient, norm_inter_medicine, norm_polish_medicine, norm_dose))
    #conn.commit()

def put_data_to_db(db_name, records):
    # Create connection to DB
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for r in records:
        sex = get_with_add_sex(conn, r[2])
        patient = get_with_add_patient(conn, r[1], r[3], r[4], sex)
        try:
            add_prescription(conn, r[0], patient, r[5], r[6], r[7])
        except:
            print r

    conn.commit()
    conn.close()

def show_db_content(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for row in c.execute('SELECT * FROM patient ORDER BY id DESC LIMIT 10'):
        print row

    for row in c.execute('SELECT * FROM prescription ORDER BY id DESC LIMIT 10'):
        print row

    for row in c.execute('SELECT * FROM sex ORDER BY id'):
        print row

    conn.close()

if __name__ == '__main__':
    db_name = '../test.db'
    #records = read_data_from_file('neuro_sample.csv')
    records = read_data_from_file('neuroleptyki_cleared.csv')
    create_tables(db_name)
    put_data_to_db(db_name, records)
    show_db_content(db_name)