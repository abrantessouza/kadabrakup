# -*- coding: cp1252 -*-
import os
import MySQLdb as sql

conn = sql.connect('127.0.0.1', 'kadabra', '', 'kadabrakup');
conn.text_factory = str
cur = conn.cursor()

directory = r"\\10.10.1.40\d\MassHunter"


def modification_date(filename): #RETORNA O TIMESTAMP DO ARQUIVO MOTIDICADO
    t = os.path.getmtime(filename) 
    return int(t)
i = 0
filesCounter = 0
dict_path = {}
dict_db = {}
limitI = 0
limitF = 700
queryCheckFile = "SELECT caminhoArquivo, timestamp FROM arquivos WHERE idPasta = 21"
queryRawGlobal = queryCheckFile
cur.execute(queryCheckFile)
totalFetchFilesSQL = cur.fetchall()
totalFetchFilesSQL = len(totalFetchFiles)
print totalFetchFilesSQL

for path, folders, files in os.walk(directory):
    for f in files:
        filesCounter = filesCounter + 1
        join_path = os.path.join(path,f)
        dict_path[join_path] = modification_date(join_path)
        print i
        print limitF, limitI, (limitF - limitI)
        limit = limitF - limitI
        if i == limit:            
            queryCheckFile +=  " LIMIT %d, %d " % (limitI, limitF)
            cur.execute(queryCheckFile)
            testeFileTimeStamp = cur.fetchall()
            for tp in testeFileTimeStamp: #LIST FORM SQL STATMENT
                dict_db[tp[0]] = tp[1]
                
            for dp in dict_path:
                if dp in dict_db:
                    print "Comparar o timestamp se tiver diferença, copia e update na tabela"
                else:
                    print "COPIAR NOVO ARQUIVO E INSERE DADOS NA TABLEA"
            queryCheckFile = queryRawGlobal                     
            dict_path = {}
            dict_db = {}
            if filesCounter > totalFetchFilesSQL:
                limitI = limitF
                limitF = totalFetchFilesSQL
            else:
                limitI = limitF
                limitF += 700
            i = 0
        i = i + 1
            
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

    
