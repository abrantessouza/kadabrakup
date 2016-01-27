# -*- coding: cp1252 -*-
#import sqlite3 as sql
import sys, os, shutil, win32api, win32con
import zipfile
from datetime import datetime
import MySQLdb as sql

queryComputador = "SELECT * FROM computador WHERE heavy = 0 AND ignory = 0 ORDER BY name ASC"

conn = sql.connect('127.0.0.1', 'root', '', 'kadabrakup');
#conn = sql.connect('pwnbackup.db',check_same_thread=False) #CONECTA AO BD SQLITE
conn.text_factory = str

def modification_date(filename): #RETORNA O TIMESTAMP DO ARQUIVO MOTIDICADO
    t = os.path.getmtime(filename) 
    return int(t)

def gravaLog(msg, idComputador):
    msg = msg.replace("\\","/")
    msg = msg.replace("'", "''")
    cur = conn.cursor()
    dataHoje = datetime.now()
    dateHojeBr = str(dataHoje.day) + "/" + str(dataHoje.month) + "/" + str(dataHoje.year) + "_"+ str(dataHoje.hour) +":"+ str(dataHoje.minute)
    try:
        cur.execute("INSERT INTO logs (mensagem, idComputador, data) VALUES ('%s', %d, '%s') " % (str(msg), int(idComputador), dateHojeBr) )
        conn.commit()
    except Exception as e:
        mensg = "Erro ao gravar o Log "+str(e)
        print mensg
        try:
            cur.execute("INSERT INTO logs (mensagem, idComputador, data) VALUES ('%s', %d, '%s') " % (str(mensg), int(idComputador), dateHojeBr) )
            conn.commit()
        except:
            conn.commit()
            pass        
    except:
        print "Erro ao gravar o log"

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


def calcPercentagemFiles(i, totalFiles):
    percent = float( i * 100 / totalFiles)
    return  str(percent) + "%" 



def zipdir(path, ziph):   
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def makeZipMove(nameFile, folderDestTemp, folderDest, computadadorNome, idComputador):
    cur = conn.cursor()
    dataHoje = datetime.now()
    os.chmod(folderDestTemp, 0o777)        
    #gravaLog("Forcing Zip the Directory |  Erro: "+str(e), idComputador)
    zf = zipfile.ZipFile(nameFile+'.zip', mode='w', allowZip64=True)
    zipdir(folderDestTemp, zf)
    zf.close()
    shutil.move(nameFile+".zip",folderDest)
    try:
        shutil.rmtree(folderDestTemp)
    except Exception as e:
        print str(e)
        for path, dirr, files in os.walk(folderDestTemp):
            for f in files:
                try:
                    os.chmod(os.path.join(path, f),0o777) 
                    os.remove(os.path.join(path, f))
                except:
                    pass
    cur.execute("UPDATE computador SET status='Finalizado com Sucesso "+str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day)+" ' WHERE id='"+str(idComputador)+"'")
    conn.commit()
    gravaLog("BACKUP do "+computadadorNome+" FINALIZADO", idComputador)
   

def backupFull(idComputador):
    queryComputador = "SELECT * FROM computador"
    if idComputador:
        queryComputador += " WHERE id = %d" % (int(idComputador))
    else:
        pass
    cur = conn.cursor()
    cur.execute(queryComputador)
    comp = cur.fetchall()
    for c in comp:
        #totalFiles = getTotalFilesSource(c[0])
        folderDest = c[2]+"\\"+c[1]+"\\Backup"
        try:
            shutil.rmtree(folderDest)
        except:
            pass
        queryFolders = "SELECT * FROM copiarpasta WHERE idComputador = %d " % (c[0])
        dataHoje = datetime.now()
        dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)        
        cur.execute(queryFolders)
        folders = cur.fetchall()        
        cur.execute("UPDATE computador SET status='Preparando Backup' WHERE id = "+str(c[0]))
        conn.commit()
        j = 0
        for f in folders:
            root = f[2].split("\\")
            del root[0]
            del root[0]
            del root[0]
            root = "\\".join(root)
            print root
            cur.execute("UPDATE computador SET status='Fazendo Backup' WHERE id = "+str(c[0]))           
            gravaLog("BACKUP FULL do "+c[1]+" iniciado -> "+f[2], c[0])
            cur.execute("DELETE FROM arquivos WHERE idPasta = %d " % (f[0]))
            #cur.execute("VACUUM;")
            conn.commit()            
            folderDest = c[2]+"\\"+c[1]+"\\Backup" + "\\" + root  #pasta de destino
            try:
                shutil.copytree(f[2], folderDest)
            except:
                msg = "Falha ao gravavar log"
                gravaLog(msg, idComputador)
        
            for path, dirr, files in os.walk(f[2]):
                for fi in files:                    
                    sourceFileRaw = os.path.join(path, fi)
                    sourceFile = sourceFileRaw.replace("'","''")
                    try:
                        cur.execute("INSERT INTO arquivos (idPasta, caminhoArquivo, timestamp) VALUES ('"+str(f[0])+"', '"+sourceFile.replace("\\","\\\\")+"', '"+str(modification_date(sourceFileRaw))+"' )" )
                        
                    except Exception as e:
                        print sourceFile
                        print str(e)            
        cur.execute("UPDATE computador SET status='Compactando os Arquivos' WHERE id = "+str(c[0]))
        conn.commit()
        nameFile = nameFile = c[1]+"_full_"+dateHoje
        folderDest = c[2]+"\\"+c[1]+"\\Backup"
        makeZipMove(nameFile, folderDest, c[2]+"\\"+c[1], c[1], c[0])
           
                
def backupIncremental(idComputador):
    gravaLog("BACKUP INCREMENTAL do iniciado", idComputador)
    cur = conn.cursor()
    queryComputador = "SELECT * FROM computador"
    cur.execute("UPDATE computador SET status='Fazendo Backup Incremental' WHERE id = "+str(idComputador))
    conn.commit()
    #totalFiles = getTotalFilesSource(idComputador)
    if idComputador:
        queryComputador += " WHERE id = %d" % (int(idComputador))
    else:
        pass
    cur = conn.cursor()
    cur.execute(queryComputador)
    comp = cur.fetchall()
    for c in comp:
        nomeComputador = c[1]
        folderDest = c[2]+"\\"+c[1]+"" #pasta de destino
        folderDestiny = folderDest + "\\Backup\\"
    try:
        shutil.rmtree(folderDestiny)
    except:
        pass
    #executa o backup incremental
    
    queryFolders  = "SELECT * FROM copiarpasta WHERE idComputador = % d" % (idComputador)
    dataHoje = datetime.now()
    dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)
    
    cur.execute(queryFolders)
    folders = cur.fetchall()
    
    j = 0
    i = 0
   
    for f in folders:
        for path, dirr, files in os.walk(f[2]):
            for fi in files:   
                fullPathRaw = os.path.join(path,fi)                
                rootfolder = fullPathRaw.split("\\")
                del rootfolder[0]
                del rootfolder[0]
                del rootfolder[0]                
                rootfolder = "\\".join(rootfolder)
                fullPath = fullPathRaw.replace("'","''")
                queryCheckFile = "SELECT * FROM arquivos WHERE idPasta = %d AND caminhoArquivo = '%s' " % (f[0], fullPath.replace("\\","\\\\"))
                cur.execute(queryCheckFile)
                rowFile = cur.fetchall()
                makeDestiny = folderDestiny+rootfolder                
                if len(rowFile) < 1:
                    try:
                        makeDestiny = makeDestiny.split("\\")                        
                        del makeDestiny[-1]
                        makeDestiny = "\\".join(makeDestiny)
                        print "Criando Novo "+makeDestiny
                        os.makedirs(makeDestiny)
                    except Exception as e:
                        print "PEi!!!"
                        print str(e)
                    try:
                        
                        shutil.copy2(fullPath.replace("''","'"),makeDestiny)
                        with conn:
                            try:
                                cur.execute("INSERT INTO arquivos (idPasta, caminhoArquivo, timestamp) VALUES ('"+str(f[0])+"', '"+fullPath.replace("\\","\\\\")+"', '"+str(modification_date(fullPathRaw))+"' )" )
                                conn.commit()
                            except :
                                pass
                    except Exception as e:
                        gravaLog(str(e), idComputador) 
                else:
                    makeDestiny = folderDestiny+rootfolder
                    idArquivos, idPasta, caminho, timeStampDb = rowFile[0]
                    timeStampDb = str(int(timeStampDb))
                    try:
                        timeStampRemote = str(int(modification_date(fullPathRaw.replace("\\","\\\\"))))
                    except:
                        timeStampRemote = timeStampDb                   
                    
                    if timeStampRemote != timeStampDb: #COMPARAÇÃO COM AS DADAS DE MODIFICAÇOES
                        with conn:
                            cur.execute("UPDATE arquivos SET timestamp = '"+str(modification_date(fullPathRaw))+"' WHERE caminhoArquivo ='"+fullPath.replace("\\","\\\\")+"'")
                            conn.commit()
                        try:
                            makeDestiny = makeDestiny.split("\\")
                            del makeDestiny[-1]
                            makeDestiny = "\\".join(makeDestiny)
                            print "Substituindo "+makeDestiny
                            subdirs = path.replace(f[2],"")                                                         
                            os.makedirs(makeDestiny)
                           
                        except Exception as e:
                            print str(e)
                        try:
                            subdirs = path.replace(f[2],"")                             
                            shutil.copy2(fullPathRaw,makeDestiny)
                        except Exception as e:
                            print str(e)                   
     
    nameFile =  nomeComputador+"_incremental_"+dateHoje    
    try:
        makeZipMove(nameFile, folderDestiny, folderDest, nomeComputador, idComputador)
    except Exception as e:
        gravaLog("Sem Backup para gravar", c[0])


def counterFiles(idComputador):
    queryFoldersCopy = "SELECT * FROM copiarpasta WHERE idComputador = %d " % (idComputador)
    arrSum = []
    with conn:
        cur = conn.cursor()
        cur.execute(queryFoldersCopy)
        folders = cur.fetchall()
        for f in folders:
            queryFiles = "SELECT COUNT(*) as count, 'teste' FROM arquivos WHERE idPasta = %d " % (f[0])
            cur.execute(queryFiles)
            totalFiles = cur.fetchall()            
            countFile, teste =   totalFiles[0]
            arrSum.append(countFile)           
        return sum(arrSum)
            
            

    


def taskBackup():
    with conn:
        cur = conn.cursor() #ATIVA O CURSOR DO SQLITE
        cur.execute(queryComputador) #EXECUTA A QUERY PARA LISTAR OS ALIAS DAS MAQUINAS REMOTAS QUE DEVEM EXECUTAR O BACKUP
        comp = cur.fetchall()
        for c in comp: #LISTA DE COMPUTADORES
            lenRowsFiles = counterFiles(c[0])
            queryFolders = "SELECT * FROM copiarpasta "
            dataHoje = datetime.now()
            dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)
            gravaLog("Preparacao do BACKUP do computador "+c[1]+" ", c[0])
            folderDest = c[2]+"\\"+c[1]+"\\Backup" #pasta de destino        
            queryFolders += "WHERE idComputador = %d " % (c[0])  #QUERY PARA LISTAR AS PASTAS QUE DEVEM SER FEITAS OS BACKUPS DA MAQUINA REMOTA       
            if cur.execute(queryFolders):
               queryFolders = "SELECT * FROM copiarpasta "
            folders = cur.fetchall()
            runBackup = False
            for f in folders:
                if os.path.isdir(f[2]):                    
                    runBackup = True
            if runBackup:
                print lenRowsFiles
                cur.execute("UPDATE computador SET status='Preparando para iniciar o Backup' WHERE id = "+str(c[0]))
                conn.commit()
                if lenRowsFiles == 0:
                    backupFull(c[0])
                else:
                    backupIncremental(c[0])
                conn.commit()
            else:
                cur.execute("UPDATE computador SET status='Falha no Backup' WHERE id = "+str(c[0]))
                conn.commit()
                gravaLog("Verifique se o computador remoto esta desligado ", str(c[0]))

             
       
                
              
          
                
                    
                                                        
                            
                         
                         
                 
               
        
        
