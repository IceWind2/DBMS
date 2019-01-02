import databaseInterface as db
import json

flag = False
token = None


def sign_in():
    global token, flag
    if token is not None:
        print('You are already logged in')
        return
    login = input('\nLogin\n')
    password = input('\nPassword\n')
    try:
        token = db.login(json.dumps({'login': login, 'password': password}))
    except Exception as exc:
        print(exc)
    return


def finish():
    global flag, token
    token = None
    flag = True
    return


def add_entry():
    global token
    file_name = input('File name:\n')
    with open(file_name, 'rt', encoding='utf-8-sig') as f:
        data = f.read().split('\n')
    for obj in data:
        obj = obj.split('; ')
        P = obj[0].split(', ')
        C = obj[1].split(', ')
        T = obj[2].split(', ')

        atrsP = db.config(section='patient')
        atrsC = db.config(section='condition')
        atrsT = db.config(section='treatment')

        patient_data = {}
        condition_data = {}
        treatment_data = {}

        for ind in range(len(atrsP)):
            patient_data[atrsP[ind]] = P[ind]

        for ind in range(len(atrsT)):
            treatment_data[atrsT[ind]] = T[ind]

        for ind in range(len(atrsC)):
            condition_data[atrsC[ind]] = C[ind]

        try:
            db.add_entry(json.dumps(patient_data, ensure_ascii=False), json.dumps(condition_data, ensure_ascii=False), json.dumps(treatment_data, ensure_ascii=False), token)
            print('Patient {} successfully added'.format(patient_data['name']))
        except Exception as exc:
            if exc == 'list index out of range':
                exc = 'Wrong format'
            print(exc)
            db.roll_back()
    return


def add_rating():
    global token
    file_name = input('File name:\n')
    with open(file_name, 'rt', encoding='utf-8-sig') as f:
        data = f.read().split('\n')
    for obj in data:
        obj = obj.split(', ')
        rating_data = {
            'name': obj[0],
            'date': obj[1],
            'data': [int(x) for x in obj[2:6]] + [float(obj[6])] + [int(obj[7])] + [float(obj[8])]
        }
        try:
            db.add_rating(json.dumps(rating_data, ensure_ascii=False), token)
            print('Rating for {} have been successfully added'.format(rating_data['name']))
        except Exception as exc:
            if exc == 'list index out of range':
                exc = 'Wrong format'
            print(exc)
            db.roll_back()


def add_treatment():
    global token
    file_name = input('File name:\n')
    with open(file_name, 'rt', encoding='utf-8-sig') as f:
        data = f.read().split('\n')
    for obj in data:
        obj = obj.split(', ')
        patient_data = {
            'name': obj[0],
            'birth_date': obj[1]
        }

        treatment_data = {}
        atrsT = db.config(section='treatment')
        for ind in range(len(atrsT)):
            treatment_data[atrsT[ind]] = obj[ind + 2]
        treatment_data['change_reason'] = obj[7]
        try:
            db.add_treatment(json.dumps(patient_data, ensure_ascii=False), json.dumps(treatment_data, ensure_ascii=False), token)
            print('New treatment for {} successfully added'.format(patient_data['name']))
        except Exception as exc:
            if exc == 'list index out of range':
                exc = 'Wrong format'
            print(exc)
            db.roll_back()

    return


def add_doctor():
    global token
    file_name = input('File name:\n')
    with open(file_name, 'rt', encoding='utf-8-sig') as f:
        data = f.read().split('\n')
    for obj in data:
        obj = obj.split(', ')
        doctor_data = {}
        atrs = db.config(section='doctor')
        for ind in range(len(atrs)):
            doctor_data[atrs[ind]] = obj[ind]

        try:
            db.add_doctor(json.dumps(doctor_data, ensure_ascii=False), token)
            print('Doctor {} successfully added'.format(doctor_data['name']))
        except Exception as exc:
            print(exc)


def remove():
    global token
    name = input('Name of doctor:\n')
    db.remove_doctor(json.dumps({'name': name}, ensure_ascii=False), token)
    print('Doctor {0} have been removed'.format(name))
    return


def get_patients():
    global token
    with open('patients_result.json', 'wt', encoding='utf-8-sig') as f:
        f.write(db.get_patients(token))
    print('\nResults have been put in file \'patients_result.json\'')
    return


def get_rating():
    global token
    with open('rating_result.json', 'wt', encoding='utf-8-sig') as f:
        f.write(db.get_rating(token))
    print('\nResults have been put in file \'rating_result.json\'')
    return


def get_medicine():
    global token
    with open('medicine_result.json', 'wt', encoding='utf-8-sig') as f:
        f.write(db.get_medicine(token))
    print('\nResults have been put in file \'medicine_result.json\'')
    return


def log_out():
    global token
    token = None
    return


def comm_list():
    for key in command.keys():
        print(key)
    return


def create():
    db.create_database()
    db._cur.execute('insert into doctor(name, access, login, password) Values(\'Head doctor\', 3,  \'qwerty\', \'12345\');')
    db._cur.execute('insert into doctor(name, access, login, password) Values(\'Doctor\', 0, \'asdf\', \'12345\');')
    db._conn.commit()
    return


def assign():
    global token
    dName = input('Doctor:\n')
    pName = input('Patient:\n')
    data = {
        'doctor': dName,
        'patient': pName
    }
    db.assign(json.dumps(data, ensure_ascii=False), token)
    print('Patient {0} assigned to {1}'.format(pName, dName))
    return


def unassign():
    global token
    dName = input('Doctor:\n')
    pName = input('Patient:\n')
    data = {
        'doctor': dName,
        'patient': pName
    }
    db.unassign(json.dumps(data, ensure_ascii=False), token)
    print('Patient {0} unassigned from {1}'.format(data['patient'], data['doctor']))
    return

command = {
    'log in': sign_in,
    'exit': finish,
    'add patient': add_entry,
    'add rating': add_rating,
    'add treatment': add_treatment,
    'add doctor': add_doctor,
    'get patients': get_patients,
    'get rating': get_rating,
    'get medicine': get_medicine,
    'remove': remove,
    'log out': log_out,
    'help': comm_list,
    'create': create,
    'assign': assign,
    'unassign': unassign
}


if __name__ == '__main__':
    db.connect()
    while not flag:
        comm = input('\nInput command\n')

        if comm not in command:
            print("\nWrong command. Type help to see the list of commands")
        else:
            if comm != 'exit' and comm != 'log in' and  comm != 'help' and token is None and comm != 'create':
                print('\nLog in first')
            else:
                try:
                    command[comm]()
                except Exception as ex:
                    print(ex)
                    db.roll_back()
    db.end()
