# -*- coding: cp1252 -*-
import os
import MySQLdb as sql

conn = sql.connect('127.0.0.1', 'kadabra', '', 'kadabrakup');
conn.text_factory = str
cur = conn.cursor()

directory = r"\\10.10.0.62\htdocs\webservices\sistema"





def getTotalFilesSource(idComputador):
    countFiles = True
    cur = conn.cursor()
    queryPasta = "SELECT * FROM copiarpasta WHERE idComputador = %d " %(idComputador)
    cur.execute(queryPasta)
    folders = cur.fetchall()
    totalFiles = 0
    i = 0
    while countFiles:
        for fo in folders:
            totalFiles = totalFiles + len([fil for path, dirr, fi in os.walk(fo[02]) for fil in fi]  )
            i = i+1
            if len(folders) == i:
                countFiles = False
                return totalFiles

def modification_date(filename): #RETORNA O TIMESTAMP DO ARQUIVO MOTIDICADO
    t = os.path.getmtime(filename) 
    return int(t)

i = 0
filesCounter = 0
dict_path = {}
dict_db = {}
limitI = 0
limitF = 300
queryCheckFile = "SELECT caminhoArquivo, timestamp FROM arquivos WHERE idPasta = 5"
queryRawGlobal = queryCheckFile
cur.execute(queryCheckFile)
totalFetchFilesSQL = cur.fetchall()


#totalRemoteFiles =  getTotalFilesSource(5)

for path, folders, files in os.walk(directory):
    for f in files:
        filesCounter = filesCounter + 1
        join_path = os.path.join(path,f)        
        for x, y in totalFetchFilesSQL:
            if x == join_path:
                #se timestamp_sql > timestamp_remoto == copia arquivo e atualiza table
            else:
                #copia arquivo e insere na tabela
                
     
            
"""                   
print "Carregando dados da tabela"   
queryCheckFile = "SELECT caminhoArquivo, timestamp FROM arquivos WHERE idPasta = 19"
cur.execute(queryCheckFile)
testeFileTimeStamp = cur.fetchall()
for tf in testeFileTimeStamp:                
    dict_db[tf[0]] = tf[1]

print dict_db[0]
print dict_path[0]
"""

    
