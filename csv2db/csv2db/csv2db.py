import csv
import re
import sqlite3
import json

def isfloat(value):
    """Check if provided argument is float.
    
    Parameters:
    value - value to check
    """

    try:
        float(value)
        return True
    except ValueError:
        return False

def read_data_from_file(file_path):
    """Read data from source csv file and return an array of rows.

    Parameters:
    file_path - path to csv file
    """

    print "Reading csv file"
    records = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        # Skip headers
        next(reader, None)
        for row in reader:
            records.append(row)
            if not isfloat(row[7]):
                print len(records), row[7]
                raw_input("Press Enter to continue...")
    return records

def save_json(object, path):
    """Save object to json file.

    Parameters:
    object - object to save
    path   - name of json file
    """

    print 'Saving to json'
    with open(path, 'w') as f:
        json.dump(object, f)

def create_tables(db_name):
    """Create tables in sqlite database.

    Parameters:
    db_name - name of the database file
    """

    # Create connection to DB
    print "Creating database"
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
    c.execute('''CREATE TABLE prescription_heart (
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
    """Normalize date to proper format.

    Parameters:
    date - date to normalize
    """

    pattern = re.compile(r'(\d+)-(\d+)-(\d+)')
    match = re.search(pattern, date)
    if match:
        l = [d if len(d) > 1 else '0'+d for d in match.groups()]
        return '/'.join(l)
    raise Exception('Cannot convert date: %s', date)

def normalizer(data, is_text=True):
    """Normalize general data to get rid of 'None' and 'brak danych'.

    Parameters:
    data    - data to normalize
    is_text - flag wheter provided data is text data
    """

    if data is None or data == 'brak danych' or len(data) == 0:
        return 'NULL'
    else:
        return "'%s'" % data if is_text else data

def get_with_add_sex(conn, sex_name):
    """Get sex id from database. If sex doesn't exist in database then add it.

    Parameters:
    conn     - database connection object
    sex_name - text name of the sex
    """

    # Find sex
    c = conn.cursor()
    norm_sex = normalizer(sex_name)
    s = next(c.execute('SELECT id FROM sex WHERE name = %s' % norm_sex), None)

    if s is None and norm_sex != 'NULL':
        c.execute('INSERT INTO sex (name) VALUES (%s)' % norm_sex)
        #conn.commit()
        s = next(c.execute('SELECT id FROM sex WHERE name = %s' % norm_sex), None)
    return s[0] if s is not None else None

def get_patient(conn, patient_id, non_existing_patients_list):
    """Get patient id from database.

    Parameters:
    conn                       - database connection object
    patient_id                 - text id of the patient obtained from input file
    non_existing_patients_list - list of patient_ids that were not found in database
    """

    c = conn.cursor()
    norm_patient_id = normalizer(patient_id)
    s = next(c.execute('SELECT id FROM patient WHERE patient_id = %s' % norm_patient_id), None)

    if s is None:
        print 'No patient with id:', patient_id
        non_existing_patients_list.append(patient_id)

    return s[0] if s is not None else None

def get_with_add_patient(conn, patient_id, birth_date, death_date, sex):
    """Get patient id from database. If patient doesn't exist in database then add him.

    Parameters:
    conn       - database connection object
    patient_id - text id of the patient obtained from input file
    birth_date - patient's birth date
    death_date - patient's death date
    sex        - patient's sex id
    """

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

def add_prescription(conn, table, date, patient, international_medicine_name, polish_medicine_name, dose):
    """Add presctiption to database.

    Parameters:
    conn                        - database connection object
    table                       - database table name to add presctiption to
    date                        - prescription's date
    patient                     - patient's id in database
    international_medicine_name - international name of the medicine
    polish_medicine_name        - polish name of the medicine
    dose                        - dose of the medicine
    """

    c = conn.cursor()
    norm_date = normalizer(normalize_date(date))
    norm_patient = normalizer(patient) if patient is None else patient
    norm_inter_medicine = normalizer(international_medicine_name)
    norm_polish_medicine = normalizer(polish_medicine_name)
    norm_dose = normalizer(dose)
    
    c.execute('INSERT INTO %s (date, patient, international_medicine_name, polish_medicine_name, dose) VALUES (%s, %s, %s, %s, %s)' %
              (table, norm_date, norm_patient, norm_inter_medicine, norm_polish_medicine, norm_dose))
    #conn.commit()

def put_data_to_db(db_name, records, records_heart):
    """Put data read from csv to database.

    Parameters:
    db_name       - name of database file
    records       - data read from csv file with neuroleptic prescriptions
    records_heart - data read from csv file with cardio prescriptions
    """

    # Create connection to DB
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    i = 0
    for r in records:
        i += 1
        if i % 1000 == 0:
            print "{0}/{1} iterations done".format(i, len(records))
        if i % 10000 == 0:
            conn.commit()
        sex = get_with_add_sex(conn, r[2])
        patient = get_with_add_patient(conn, r[1], r[3], r[4], sex)
        try:
            add_prescription(conn, 'prescription', r[0], patient, r[5], r[6], r[7])
        except:
            print r

    print ''
    print '################################################'
    print 'Prescriptions done. Starting heart prescriptions'
    print '################################################'
    print ''

    non_existing_patients_list = []
    i = 0
    for r in records_heart:
        i += 1
        if i % 1000 == 0:
            print "{0}/{1} iterations done".format(i, len(records_heart))
        if i % 10000 == 0:
            conn.commit()
        patient = get_patient(conn, r[1], non_existing_patients_list)
        if patient is not None:
            add_prescription(conn, 'prescription_heart', r[0], patient, r[5], r[6], r[7])
    save_json(non_existing_patients_list, 'non_existing_patients.json')

    conn.commit()
    conn.close()

def show_db_content(db_name):
    """Show last 10 elements of each table in database.

    Parameters:
    db_name - name of database file
    """

    print "Result"
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for row in c.execute('SELECT * FROM sex ORDER BY id'):
        print row

    for row in c.execute('SELECT * FROM patient ORDER BY id DESC LIMIT 10'):
        print row

    for row in c.execute('SELECT * FROM prescription ORDER BY id DESC LIMIT 10'):
        print row

    for row in c.execute('SELECT * FROM prescription_heart ORDER BY id DESC LIMIT 10'):
        print row

    conn.close()

if __name__ == '__main__':
    db_name = '../nasercowe.db'
    #records = read_data_from_file('neuro_sample.csv')
    records = read_data_from_file('neuroleptyki_cleared.csv')
    records_heart = read_data_from_file('nasercowe_cleared.csv')
    create_tables(db_name)
    put_data_to_db(db_name, records, records_heart)
    show_db_content(db_name)