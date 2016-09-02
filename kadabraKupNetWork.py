# -*- coding: cp1252 -*-
#import sqlite3 as sql

#import sqlite3 as sql
import sys, os, shutil, win32api, win32con
import zipfile, zlib
import glob
from datetime import datetime
import MySQLdb as sql
import time

queryComputador = "SELECT * FROM computador WHERE heavy = 0 AND ignory = 0 ORDER BY name ASC"

conn = sql.connect('127.0.0.1', 'root', '', 'kadabrakup');
conn.ping(True) #AVOID TO GET "MYSQL GONE AWAY"
#conn = sql.connect('pwnbackup.db',check_same_thread=False) #CONNECT INTO SQLITE DATABASE
conn.text_factory = str

def modification_date(filename): #MAC GYVER FUNCTION RETURN THE TIMESTAMP OF MODIFICATED DATE FILE
    t = 0
    try:
        t = os.path.getmtime(filename)
    except:
        makeDestiny = "E:\\CopiaChem\\temp"
        try:
            shutil.rmtree(makeDestiny)            
        except:
            pass
        os.makedirs(makeDestiny)
        fullPathDestiny, fullPathFile = os.path.split(filename)
        newNameFile = fullPathFile.split(".")
        newNameFile = newNameFile[0][:10] + "." + newNameFile[1] #SUBSTRING THE NAME FILE TO COPY
        makeDestiny = os.path.join(makeDestiny,newNameFile.replace(" ",""))
        cmdDir = 'forceCopyFile.bat "%s" "%s" "%s" ' % (fullPathDestiny, fullPathFile, makeDestiny) #CALLS THE BATCH FILE TO MAKE A FORCE COPY USING CMD
        os.system(cmdDir)
        if os.path.isfile(makeDestiny):
            t = os.path.getmtime(makeDestiny)
            folder, file_path = os.path.split(makeDestiny)
            shutil.rmtree(folder)
    return int(t)

def gravaLog(msg, idComputador): #RECORD LOG IN DATABASE
    msg = msg.replace("\\","/")
    msg = msg.replace("'", "''")
    cur = conn.cursor()
    dataHoje = datetime.now()
    dateHojeBr = str(dataHoje.day) + "/" + str(dataHoje.month) + "/" + str(dataHoje.year) + "_"+ str(dataHoje.hour) +":"+ str(dataHoje.minute)    
    try:
        with conn:
            cur.execute("INSERT INTO logs (mensagem, idComputador, data) VALUES ('%s', %d, '%s') " % (str(msg), int(idComputador), dateHojeBr) )
            conn.commit()
    except Exception as e:
        mensg = "Erro ao gravar o Log "+str(e)
        print mensg
        try:
            with conn:
                cur.execute("INSERT INTO logs (mensagem, idComputador, data) VALUES ('%s', %d, '%s') " % (str(mensg), int(idComputador), dateHojeBr) )
                conn.commit()
        except:
            with conn:
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



def zipdir(path, ziph):   # ZIP AND COMPRESS BACKUP FOLDER
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), compress_type=zipfile.ZIP_DEFLATED)

def makeZipMove(nameFile, folderDestTemp, folderDest, computadadorNome, idComputador): #IT CALLS THE ZIPDIR FUNCTION, DELETE TEMP FILES AND MOVE THE ZIP GENERATED TO DESTINY FOLDER.
    cur = conn.cursor()
    dataHoje = datetime.now()
    os.chmod(folderDestTemp, 0o777)        
    #gravaLog("Forcing Zip the Directory |  Erro: "+str(e), idComputador)
    zf = zipfile.ZipFile(nameFile+'.zip', mode='w',allowZip64=True)
    zipdir(folderDestTemp, zf)
    zf.close()
    shutil.move(nameFile+".zip",folderDest)
    #updateStatus("Finalizado "+str(dataHoje)+"", idComputador)
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
    gravaLog("BACKUP do "+computadadorNome+" FINALIZADO", idComputador)
   

def updateStatus(string, idComputador):
    with conn:
        cur = conn.cursor()
        query = "UPDATE computador SET status='%s' WHERE id = %d" % (string, int(idComputador))
        cur.execute(query)
        conn.commit()

def backupFull(idComputador): #RUN THE FULL BACKUP
    dataHoje = datetime.now()
    dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)
    with conn:       
        queryComputador = "SELECT * FROM computador"
        
        if idComputador:
            queryComputador += " WHERE id = %d" % (int(idComputador))
        else:
            pass
        cur = conn.cursor()
        cur.execute(queryComputador)
        comp = cur.fetchall()
        for c in comp:            
            folderDest = c[2]+"\\"+c[1]+"\\"+c[1]+"_full_"+dateHoje+".zip"
            if(not(os.path.exists(c[2]+"\\"+c[1]))):
                try:
                    os.makedirs(c[2]+"\\"+c[1])
                except Exception as e:
                    gravaLog(str(e).replace("\\","/"),idComputador)
            totalFiles = getTotalFilesSource(int(c[0]))            
            queryFolders = "SELECT * FROM copiarpasta WHERE idComputador = %d " % (c[0])
            dataHoje = datetime.now()
            dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)        
            cur.execute(queryFolders)
            folders = cur.fetchall()
            updateStatus("Executando Backup Full", int(idComputador))
            conn.commit()
            j = 0
            i = 0
            zf = zipfile.ZipFile(folderDest, mode='w',allowZip64=True)
    
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
                
                for path, dirr, files in os.walk(f[2]):
                    for fi in files: 
                        sourceFileRaw = os.path.join(path, fi)
                        try:
                            zf.write(sourceFileRaw, compress_type=zipfile.ZIP_DEFLATED)
                        except Exception as e:
                            gravaLog(str(e).replace("\\","/"),int(c[0]))
                        sourceFile = sourceFileRaw.replace("'","''")
                        status = calcPercentagemFiles(i, totalFiles)
                        i = i + 1
                        queryUpdateStatus = "UPDATE computador SET status=' "+status+"' WHERE id = '"+str(c[0])+"'"
                        cur.execute(queryUpdateStatus)
                        conn.commit()
                        
                        try:
                            cur.execute("INSERT INTO arquivos (idPasta, caminhoArquivo, timestamp) VALUES ('"+str(f[0])+"', '"+sourceFile.replace("\\","\\\\")+"', '"+str(modification_date(sourceFileRaw))+"' )" )
                        except Exception as e:
                            print sourceFile
                            print str(e)  
            conn.commit()
            zf.close()
            #nameFile = nameFile = c[1]+"_full_"+dateHoje
            #folderDest = c[2]+"\\"+c[1]+"\\Backup"
            #makeZipMove(nameFile, folderDest, c[2]+"\\"+c[1], c[1], c[0])
            cur.execute("UPDATE computador SET status='Finalizado "+str(dataHoje)+"' WHERE id = "+str(c[0]))


def copyIncremental(makeDestiny, fullPathRaw, fullPath, idComputador): #SIMPLE METHOD OF COPY JUST TO MAKE A CLEAN CODE     
    makeDestiny, makeDestinyFileName = os.path.split(makeDestiny)    
    if(not(os.path.exists(makeDestiny))):
        try:
            os.makedirs(makeDestiny)
        except Exception as e:
            gravaLog(str(e).replace("\\","/"),idComputador)
    try:        
        shutil.copy2(fullPath.replace("''","'"), makeDestiny)
        timestamp = modification_date(fullPathRaw)
    except Exception as e:
        #PROBABLY THE EXCEPTION OCCURIED BECAUSE THE FILE'S NAME IS TOO LARGE
        gravaLog(""+ str(e).replace("\\","/") + ". Running Force Large File Copy",idComputador)
        fullPathDestiny, fullPathFile = os.path.split(fullPath)
        newNameFile = fullPathFile.split(".")
        newNameFile = newNameFile[0][:10] + "." + newNameFile[1] #SUBSTRING THE NAME FILE TO COPY
        makeDestiny = os.path.join(makeDestiny,newNameFile.replace(" ",""))
        cmdDir = 'forceCopyFile.bat "%s" "%s" "%s" ' % (fullPathDestiny, fullPathFile, makeDestiny) #CALLS THE BATCH FILE TO MAKE A FORCE COPY USING CMD
        os.system(cmdDir)
        timestamp = modification_date(makeDestiny)
    except Exception as e:
        gravaLog("Erro ao copiar: "+ str(e).replace("\\","/"),idComputador)
    #RETURN THE TIMESTAMP OF COPIED FILE
    return str(timestamp)
    
        


                
def backupIncremental(idComputador): # RUN THE BACKUP INCREMENTAL
    gravaLog("BACKUP INCREMENTAL do iniciado", idComputador)
    cur = conn.cursor()
    queryComputador = "SELECT * FROM computador"
    updateStatus("Recolhendo Metadados...", idComputador)
    totalFiles = getTotalFilesSource(idComputador)
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
    except Exception as e:
        print str(e)
    #executa o backup incremental
    
    queryFolders  = "SELECT * FROM copiarpasta WHERE idComputador = % d" % (idComputador)
    dataHoje = datetime.now()
    dateHoje = str(dataHoje.year) + "_" + str(dataHoje.month) + "_" + str(dataHoje.day) + "_"+ str(dataHoje.hour) +"_"+ str(dataHoje.minute)
    
    cur.execute(queryFolders)
    folders = cur.fetchall()
    
    j = 0
    i = 0
   
    for f in folders:
        queryCheckFile = "SELECT id, caminhoArquivo, timestamp FROM arquivos WHERE idPasta = %d " % (f[0])
        colunas = ["id", "caminhoArquivo", "timestamp"]
        cur.execute(queryCheckFile)
        rowsFiles = cur.fetchall()
        teste = [dict(zip(colunas,rows)) for rows in rowsFiles]
        lista = list()
        status = "0%"
        for t in teste:                    
            lista.append(t['caminhoArquivo'])
        for path, dirr, files in os.walk(f[2]):
            for fi in files:   
                fullPathRaw = os.path.join(path,fi)                
                rootfolder = fullPathRaw.split("\\")
                del rootfolder[0]
                del rootfolder[0]
                del rootfolder[0]                
                rootfolder = "\\".join(rootfolder)
                fullPath = fullPathRaw.replace("'","''") 
                makeDestiny = folderDestiny+rootfolder
                status = calcPercentagemFiles(i, totalFiles)
                i = i + 1
                queryUpdateStatus = "UPDATE computador SET status= '"+status+"' WHERE id = '"+str(idComputador)+"'"                
                with conn:
                    cur.execute(queryUpdateStatus)
                    conn.commit()
                if fullPathRaw in lista:
                     for id, caminhoArquivo, timestamp in rowsFiles:
                         if fullPathRaw == caminhoArquivo:
                             #print caminhoArquivo
                             timeStampRemote = str(int(modification_date(fullPathRaw)))
                             if int(timestamp) < int(timeStampRemote):
                                 copyIncremental(makeDestiny, fullPathRaw, fullPath, idComputador)
                                 with conn:
                                    try:
                                        cur.execute("UPDATE arquivos SET timestamp = '"+str(timeStampRemote)+"' WHERE id ='"+str(id)+"'")
                                        conn.commit()
                                    except Exception as e:
                                        print "Erro ao Atualizar"
                                        print str(e)
                                 
                else:
                    with conn:
                        try:
                            timestampRemote = copyIncremental(makeDestiny, fullPathRaw, fullPath, idComputador) 
                            cur.execute("INSERT INTO arquivos (idPasta, caminhoArquivo, timestamp) VALUES ('"+str(f[0])+"', '"+fullPath.replace("\\","\\\\")+"', '"+str(timestampRemote)+"' )" )
                            conn.commit()
                            #
                        except Exception as e:
                            print "Erro ao inserir"
                            print str(e)
                            
    nameFile =  nomeComputador+"_incremental_"+dateHoje    
    try:
        updateStatus("Finalizando... "+status, idComputador)
        makeZipMove(nameFile, folderDestiny, folderDest, nomeComputador, idComputador)        
        with conn:            
            updateStatus("Finalizado "+str(dataHoje), idComputador)
            nameFile = os.path.join(folderDest, nameFile)
            queryInsertFileIncr = "INSERT INTO storeincrimental (idComputador, nomeArquivo, dataInsercao) VALUES (%d, '%s.zip', '%s')" % (idComputador, nameFile.replace("\\","\\\\"), time.strftime('%Y-%m-%d'))
            cur.execute(queryInsertFileIncr)
            conn.commit()
    except Exception as e:
        print e
        gravaLog("Sem Backup para gravar", idComputador)
        updateStatus("Finalizado, porém sem arquivos para copiar", idComputador)


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
            
            

def backupDiferencial(idComputador, nomeComputador):
    #PRIMEIRO PEGARÁ OS DADOS DE CONFIGURAÇÕES GLOBAIS E PARCIAIS
    queryGlobalSettings = "SELECT * FROM globalsettings"
    queryComputer = "SELECT interval_full, interval_incr FROM computador WHERE id = %d" % (idComputador)
    with conn:
        cur = conn.cursor()
        cur.execute(queryComputer)        
        daysIncr = 0
        daysIncrComp = 0
        infoComputador = cur.fetchall()
        for inf in infoComputador:
             daysIncrComp = inf[1]             
        if daysIncrComp == 0:
            cur.execute(queryGlobalSettings)
            infoGlobalSetting = cur.fetchall()
            for inf in infoGlobalSetting:
                daysIncr = inf[2]
        else:
            daysIncr = daysIncrComp

        if daysIncr == 0 and daysIncrComp == 0:
            daysIncr = 7
        else:
            pass        
          
    print nomeComputador + str(daysIncr)
    queryFilesBackupIncr = "SELECT * FROM storeincrimental WHERE idComputador = %d " % (idComputador)
    #EXECUTA O BACKUP DIFERENCIAL DEPENDENDO DA CONDIÇÃO DO BLOCO ACIMA
    with conn:
        cur = conn.cursor()
        cur.execute(queryFilesBackupIncr)
        rows = cur.fetchall()
        folderDest = ""
        print len(rows)
        if len(rows) > daysIncr:
            updateStatus("Executando Backup Diferencial", idComputador)
            diffTempPath = os.getcwd()
            diffTempPath = diffTempPath + "\\tempDiff"
            if os.path.isdir(diffTempPath) == False:
                os.mkdir(diffTempPath)
            for r in rows:
                folderDest = r[2]
                splitterFolderDest = folderDest.split("\\")
                del splitterFolderDest[len(splitterFolderDest) - 1]
                folderDest = "\\".join(splitterFolderDest)
                try:
                    with zipfile.ZipFile(r[2],"r") as z:
                        z.extractall(diffTempPath)
                except:
                    pass
            nameFile = nomeComputador+"_diferencial_"+time.strftime('%Y%m%d_%H%M')
            zf = zipfile.ZipFile(nameFile+'.zip', mode='w',allowZip64=True)
            zipdir("tempDiff", zf)
            zf.close()
            shutil.move(nameFile+".zip",folderDest)
            queryDelete = "DELETE FROM storeincrimental WHERE idComputador = %d" %(idComputador)
            cur.execute(queryDelete)                       
            try:
                shutil.rmtree(diffTempPath)
            except Exception as e:
                print str(e)
            


def taskBackup():   
    with conn:        
        cur = conn.cursor() #ATIVA O CURSOR DO SQLITE
        cur.execute(queryComputador) #EXECUTA A QUERY PARA LISTAR OS ALIAS DAS MAQUINAS REMOTAS QUE DEVEM EXECUTAR O BACKUP
        comp = cur.fetchall()
        print comp
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
                    backupDiferencial(c[0], c[1])
                    backupIncremental(c[0])
                conn.commit()
            else:
                cur.execute("UPDATE computador SET status='Falha no Backup' WHERE id = "+str(c[0]))
                conn.commit()
                gravaLog("Verifique se o computador remoto esta desligado ", str(c[0]))
           

                
                    
                                                        
                            
                         
                         
                 
               
        
        
