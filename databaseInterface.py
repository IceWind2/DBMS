import psycopg2
import json
from config import _config
from config import _config_data
from scripts.createDatabaseScripts import createDatabaseScripts

_conn = None
_cur = None
_cur_users = {}


def connect():  # Create connection to posgreSQL
    global _cur, _conn

    params = _config()
    _conn = psycopg2.connect(**params)
    _conn.set_client_encoding('UTF8')
    _cur = _conn.cursor()


def end():
    _conn.close()


def create_database():  # Creates tables if not existed
    global _conn, _cur
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        scripts = createDatabaseScripts()
        for script in scripts:
            _cur.execute("""
                        select exists (
                            select * from information_schema.tables 
                            where table_name = %s
                        );
                        """, (script[0],))
            if _cur.fetchone()[0] == False:
                _cur.execute(script[1])
                _conn.commit()
                print('Table {0} created'.format(script[0]))
            else:
                print('Table {0} already exists'.format(script[0]))


def get_patients(token):  # Get list of patients with medicine
    global _cur, _conn, _cur_users
    if _cur is None:
        raise Exception('Database connection is not established')
    else:
        cur_id, access, name = _login_check(token)  # Get info about current doctor
        colums = ['name', 'birth_date', 'sex', 'address', 'diagnosis', 'medicine']
        _cur.execute('''
                    select pt.name, pt.birth_date, pt.sex, pt.address, pt.diagnosis, coalesce(treatment.medicine, '------')
                    from patient as pt
                    left join condition on condition.patient_id = pt.patient_id
                    left join treatment on treatment.treatment_id = condition.treatment_id
                    where pt.patient_id in (select patient_id 
                                            from doctor_patient
                                            where doctor_id = %s
                                            ) OR
                                        %s   
                    order by pt.address DESC;
                    ''', (cur_id, access))
        _conn.commit()

        res = []
        for row in _cur.fetchall():
            tmp = {}
            for i in range(len(colums)):
                tmp[colums[i]] = str(row[i])
            res.append(tmp)
        return json.dumps(res, ensure_ascii=False)


def get_rating(token):
    global _cur, _conn, _cur_users
    if _cur is None:
        raise Exception('Database connection is not established')
    else:
        cur_id, access, name = _login_check(token)  # Get info about current doctor
        colums = ['rating_date', 'active', 'damaged', 'doctor_score', 'patient_score', 'chaq', 'soe', 'srb']
        _cur.execute('''
                        select pt.name, rt.*, tr.medicine
                        from patient as pt
                        left join rating as rt on rt.patient_id = pt.patient_id
                        left join treatment as tr on tr.treatment_id = rt.treatment_id
                        where pt.patient_id in (select patient_id 
                                                from doctor_patient
                                                where doctor_id = %s
                                                ) OR
                                            %s   
                        order by pt.name ASC;
                        ''', (cur_id, access))
        _conn.commit()

        res = []
        prev = ''
        entry = {}
        for row in _cur.fetchall():
            if row[0] != prev:
                if entry:
                    res.append(entry)
                entry = {
                    'name': row[0],
                    'data': []
                }
            tmp = {}
            for i in range(len(colums)):
                tmp[colums[i]] = str(row[i + 2])
            entry['data'].append(tmp)
            prev = row[0]
        res.append(entry)
        return json.dumps(res, ensure_ascii=False)


def get_medicine(token):  # Get list of patients with medicine
    global _cur, _conn, _cur_users
    if _cur is None:
        raise Exception('Database connection is not established')
    else:
        cur_id, access, name = _login_check(token)  # Get info about current doctor
        colums = ['birth_date', 'sex', 'diagnosis', 'uveit', 'antigen', 'rentgen_state', 'func_group', 'medicine', 'dose', 'start_date', 'side_effect', 'side_medicine', 'change_reason', 'previous_medicine']
        _cur.execute('''
                    select pt.birth_date, pt.sex, pt.diagnosis, cond.uveit, cond.antigen, cond.rengen_state, cond.func_group, tr1.medicine, tr1.dose, tr1.start_date, tr1.side_effect, tr1.side_medicine, tr1.change_reason, tr2.medicine
                    from patient as pt
                    left join condition as cond on cond.patient_id = pt.patient_id
                    left join treatment as tr1 on tr1.treatment_id = cond.treatment_id
                    left join treatment as tr2 on tr1.previous_id = tr2.treatment_id
                    where (pt.patient_id in (select patient_id 
                                            from doctor_patient
                                            where doctor_id = %s
                                            ) OR %s) AND
                          tr1.medicine is not null
                    order by tr1.medicine ASC;
                    ''', (cur_id, access))
        _conn.commit()

        res = []
        prev = ''
        entry = {}
        for row in _cur.fetchall():
            if row[7] != prev:
                if entry:
                    res.append(entry)
                entry = {
                    'medicine': row[7],
                    'patients': []
                }
            tmp = {}
            for i in range(len(colums)):
                if i == 0 or i == 7:
                    continue
                tmp[colums[i]] = str(row[i])
            entry['patients'].append(tmp)
            prev = row[7]
        res.append(entry)
        return json.dumps(res, ensure_ascii=False)


def add_entry(patientData, conditionData, treatmentData, token):  # Insert patient, condition and treatment data
    global _cur, _conn
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        cur_id, access, name = _login_check(token)

        patientData = json.loads(patientData)
        conditionData = json.loads(conditionData)
        treatmentData = json.loads(treatmentData)

        atrsP = _config_data(section='patient')
        atrsC = _config_data(section='condition')
        atrsT = _config_data(section='treatment')

        # Checking and inserting patient data

        clms = ''
        param = ''
        for atr, val in patientData.items():
            if atr not in atrsP:
                raise Exception('Invalid data')
            clms = clms + atr + ', '
            param = param + '%(' + atr + ')s, '
        clms = clms[:len(clms) - 2]
        param = param[:len(param) - 2]
        _cur.execute('insert into patient ({0}) Values ({1});'.format(clms, param), patientData)
        _cur.execute('select currval(pg_get_serial_sequence(\'patient\', \'patient_id\'));')
        PID = _cur.fetchone()[0]

        # Checking and inserting treatment data

        clms = ''
        param = ""
        for atr, val in treatmentData.items():
            if atr not in atrsT:
                raise Exception('Invalid data')
            clms = clms + atr + ', '
            param = param + '%(' + atr + ')s, '
        clms = clms[:len(clms) - 2]
        param = param[:len(param) - 2]
        _cur.execute('insert into treatment ({0}) Values ({1});'.format(clms, param), treatmentData)
        _cur.execute('select currval(pg_get_serial_sequence(\'treatment\', \'treatment_id\'));')
        TID = _cur.fetchone()[0]

        # Checking and inserting condition data

        clms = 'patient_id, '
        param = '%(patient_id)s, '
        for atr, val in conditionData.items():
            if atr not in atrsC:
                raise Exception('Invalid data')
            clms = clms + atr + ', '
            param = param + '%(' + atr + ')s, '
        clms += 'treatment_id'
        param = param + '%(treatment_id)s'
        conditionData['patient_id'] = PID
        conditionData['treatment_id'] = TID
        _cur.execute('insert into condition ({0}) Values ({1});'.format(clms, param), conditionData)
        _cur.execute('insert into doctor_patient values (%s, %s);', (cur_id, PID))

        _conn.commit()
        return


def add_rating(data, token):
    global _cur, _conn
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        data = json.loads(data)
        cur_id, access, name = _login_check(token)
        if data['name'] is None:
            raise Exception('Invalid data')

        _cur.execute('''
                    select patient_id 
                    from  patient
                    where patient.name = %s AND
                    (patient.patient_id in (select patient_id from doctor_patient where doctor_id = %s) or %s);
                     ''', (data['name'], cur_id, access))
        PID = _cur.fetchone()
        if PID is None:
            raise Exception('Patient is not found')
        PID = PID[0]

        _cur.execute('''
                    select treatment.treatment_id
                    from condition, treatment
                    where condition.patient_id = %s AND
                    condition.treatment_id = treatment.treatment_id;
                    ''', (PID,))
        TID = _cur.fetchone()
        if TID is None:
            raise Exception('Treatment is not found')
        TID = TID[0]

        _cur.execute('''
                    insert into rating values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (PID, data['date'], data['data'][0], data['data'][1], data['data'][2], data['data'][3], data['data'][4], data['data'][5], data['data'][6], TID))

        _conn.commit()
        return


def add_treatment(patientData, treatmentData, token):
    global _cur, _conn
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        patientData = json.loads(patientData)
        treatmentData = json.loads(treatmentData)
        cur_id, access, name = _login_check(token)
        atrs = _config_data(section='treatment')
        if patientData['name'] is None or patientData['birth_date'] is None:
            raise Exception('Invalid data')

        _cur.execute('''
                    select tr.treatment_id, tr.medicine, tr.dose, tr.start_date, tr.side_medicine, side_effect, pt.patient_id
                    from treatment as tr, condition as cond, patient as pt
                    where pt.name = %s AND pt.birth_date = %s AND pt.patient_id = cond.patient_id AND cond.treatment_id = tr. treatment_id AND
                    (pt.patient_id in (select patient_id from doctor_patient where doctor_id = %s) or %s);
                    ''', (patientData['name'], patientData['birth_date'], cur_id, access))
        cur_tr = _cur.fetchone()
        if cur_tr is None:
            raise Exception('Patient {} is not found'.format(patientData['name']))
        TID = cur_tr[0]

        clms = ''
        param = ''
        for atr, val in treatmentData.items():
            if atr not in atrs and atr != 'change_reason':
                raise Exception('Invalid data')
            clms = clms + atr + ', '
            param = param + '%(' + atr + ')s, '

        for ind in range(len(atrs)):
            if treatmentData[atrs[ind]] is None:
                treatmentData[atrs[ind]] = cur_tr[ind + 1]
                clms = clms + atrs[ind] + ', '
                param = param + '%(' + atrs[ind] + ')s, '
            if treatmentData[atrs[ind]] == '':
                treatmentData[atrs[ind]] = cur_tr[ind + 1]

        clms = clms + 'previous_id'
        param = param + '%(previous_id)s'
        treatmentData['previous_id'] = TID
        _cur.execute('insert into treatment ({0}) Values ({1});'.format(clms, param), treatmentData)

        _cur.execute('select currval(pg_get_serial_sequence(\'treatment\', \'treatment_id\'));')
        new_tid = _cur.fetchone()[0]
        PID = cur_tr[len(cur_tr) - 1]
        _cur.execute('''
                            update condition
                            set treatment_id = %s
                            where patient_id = %s
                            ''', (new_tid, PID))
        _conn.commit()
        return


def add_doctor(data, token):
    global _cur, _conn, _cur_users
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
         cur_id, access, name = _login_check(token)
         if access == 0:
             raise Exception('Not enough rights')

         data = json.loads(data)
         atrs = _config_data(section='doctor')
         clms = ''
         param = ''
         for atr, val in data.items():
             if atr not in atrs:
                 raise Exception('Invalid data')
             clms = clms + atr + ', '
             param = param + '%(' + atr + ')s, '
         clms = clms[:len(clms) - 2]
         param = param[:len(param) - 2]
         _cur.execute('''
                    insert into doctor({0}) Values({1})
                    '''.format(clms, param), data)
         _conn.commit()
         return


def remove_doctor(data, token):
    global _cur, _conn, _cur_users
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        data = json.loads(data)
        cur_id, access, name = _login_check(token)
        if access == 0:
            raise Exception('Not enough rights')
        _cur.execute('select exists(select doctor_id from doctor where name = %s)', (data['name'],))
        fl = _cur.fetchone()[0]
        if not fl:
            raise Exception('Doctor is not found')
        _cur.execute('''
                    delete from doctor
                    where name = %s;
                    ''', (data['name'], ))
        _conn.commit()
        return


def assign(data, token):
    global _cur, _conn, _cur_users
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        data = json.loads(data)
        cur_id, access, name = _login_check(token)
        if access == 0:
            raise Exception('Not enough rights')
        _cur.execute('select doctor_id from doctor where name = %s;', (data['doctor'],))
        DID = _cur.fetchone()
        if DID is None:
            raise Exception('Doctor is not found')
        DID = DID[0]
        _cur.execute('select patient_id from patient where name = %s;', (data['patient'],))
        PID = _cur.fetchone()
        if PID is None:
            raise Exception('Patient is not found')
        PID = PID[0]

        _cur.execute('insert into doctor_patient values(%s, %s)', (DID, PID))
        _conn.commit()
        return


def unassign(data, token):
    global _cur, _conn, _cur_users
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        data = json.loads(data)
        cur_id, access, name = _login_check(token)
        if access == 0:
            raise Exception('Not enough rights')

        _cur.execute('select doctor_id from doctor where name = %s;', (data['doctor'],))
        DID = _cur.fetchone()
        if DID is None:
            raise Exception('Doctor is not found')
        DID = DID[0]
        _cur.execute('select patient_id from patient where name = %s;', (data['patient'],))
        PID = _cur.fetchone()
        if PID is None:
            raise Exception('Patient is not found')
        PID = PID[0]

        _cur.execute('delete from doctor_patient where doctor_id = %s and patient_id = %s;', (DID, PID))

        _conn.commit()
        return



def login(data):  # login into system
    global _cur, _conn, _cur_users
    if _conn is None:
        raise Exception('Database connection is not established')
    else:
        data = json.loads(data)
        login = data['login']
        password = data['password']
        _cur.execute('''
                select doctor_id, access, name from doctor
                where login = %s and password = %s
                ''', (login, password))
        user = _cur.fetchone()
        if user is None:
            _conn.rollback()
            raise Exception('Login failed')

        token = "12345"  # ADD GENERATION
        _cur_users[token] = {'id': user[0], 'access': user[1], 'name': user[2]}  # Creates new user
        print('\nHello, {0}!'.format(user[2]))
        _conn.commit()
        return token


def _login_check(token):  # Provides info about current doctor
    global _cur_users
    if token not in _cur_users:
        raise Exception('Login check failed')
    return _cur_users[token]['id'], _cur_users[token]['access'] > 0, _cur_users[token]['name']


def roll_back():
    global _conn
    _conn.rollback()
    return


def config(section=''):
    return _config_data(section=section)
