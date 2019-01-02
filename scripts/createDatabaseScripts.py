from config import _config_data

def createDatabaseScripts():
    tables = _config_data(section='tables')
    scripts = []
    for table in tables:
        with open('./scripts/' + table + '.sql', 'r') as file:
            scripts.append((table, file.read()))
    return scripts
