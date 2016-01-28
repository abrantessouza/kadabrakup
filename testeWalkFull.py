import os

directory = r"\\10.10.1.40\d\MassHunter\GCMS\1\data"

def modification_date(filename): #RETORNA O TIMESTAMP DO ARQUIVO MOTIDICADO
    t = os.path.getmtime(filename) 
    return int(t)
i = 0
limit = 350
dict_path = {}
for path, folders, files in os.walk(directory):
    for f in files:
        join_path = os.path.join(path,f)
        dict_path[join_path] = modification_date(join_path)
        if i == limit:
            for dt in dict_path:
                print dt, dict_path[dt]
            dict_path = {}
            i = 0
        i = i + 1
