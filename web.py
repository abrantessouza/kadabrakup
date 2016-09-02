# -*- coding: cp1252 -*-
#import sqlite3 as sql
import sys, os, shutil
from datetime import datetime, timedelta
from hurry.filesize import size
from bottle import route, run, debug, template, static_file, get, request, redirect
import kadabraKupNetWork
import threading
import MySQLdb as sql
import time


queryComputador = "SELECT * FROM computador"

connt = sql.connect('127.0.0.1', 'root', '', 'kadabrakup');
cur = connt.cursor()
#conn = sql.connect('pwnbackup.db',check_same_thread=False) #CONECTA AO BD SQLITE
connt.text_factory = str
connt.ping(True)

class TaksBackup(object):
    def __init__(self):
     self.isRunning = True
     self.isRunningFull = True
     self.idComputador = ""     
     self.runningDatetime = datetime.now()
     self.runningDay = self.runningDatetime.day
     self.endRun = self.runningDatetime.day

    def runForever(self):        
         if self.isRunning == True:             
             while True:
                 if self.runningDay == self.endRun:
                     kadabraKupNetWork.taskBackup()
                     self.runningDatetime = datetime.now() + timedelta(days=1)
                     self.runningDay = self.runningDatetime.day                                              
                 endTime = datetime.now()
                 self.endRun = endTime.day
                 if self.endRun >  self.runningDay:
                     fixdate = datetime.now() + timedelta(days=1)
                     self.runningDay = fixdate.day
                     self.endRun = fixdate.day - 1                 
                 print self.endRun, self.runningDay
                 time.sleep(5)
                    
    def runBackupFull(self):
        if self.isRunningFull == True:
            kadabraKupNetWork.backupFull(self.idComputador) 
    

"""
@get('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='/bootstrap/css')
"""


l = TaksBackup()
t = threading.Thread(target = l.runForever)

def getDirectoryTotalSize(idComputador):
    queryFolders = "SELECT enderecoPasta FROM copiarpasta WHERE idComputador = %d " % (idComputador)
    totalSomaFileSize = 0
    with connt:
        cur.execute(queryFolders)
        computerFolders = cur.fetchall()
        for f in computerFolders:
            for dirpath, dirnames, filenames in os.walk(f[0]):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    totalSomaFileSize += os.path.getsize(fp)
        return totalSomaFileSize
        


@route('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='./bootstrap/css')

@route('/img/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='img/')


startBackup = False
@route('/')
def index():
    global startBackup    
    queryComputador = "SELECT * FROM computador ORDER BY name ASC"
    cur.execute(queryComputador)
    connt.commit()
    computadores = cur.fetchall()    
    btnSet = ""
    if startBackup:
        curday = time.strftime("%d")
        if l.isRunning == False:
            if l.day != curday:
                l.isRunning = True
                l.day = curday
        btnSet = "disabled='disabled'"        
    else:
        pass
        #queryUpdateAllStatus = "UPDATE computador SET status = 'None' WHERE heavy = 0 "
        #cur.execute(queryUpdateAllStatus)
        #connt.commit()

    return template('containercomputers',runingBackup = btnSet, results = computadores)

@route('/startfull')
def startFull():
    queryDeleteFull = "DELETE ar FROM arquivos ar INNER JOIN copiarpasta cp ON  ar.idPasta = cp.id INNER JOIN computador c ON c.id = cp.idComputador WHERE heavy = 0;"
    connt.ping(True)
    cur.execute(queryDeleteFull)
    connt.commit()
    redirect('/startbackup')


@route('/heavy')
def heavy():    
    redirect('http://127.0.0.1:8182')

@route('/light')
def heavy():    
    redirect('http://127.0.0.1:8180')

@route('/startbackup')
def start():
    global startBackup
    global l
    l = TaksBackup()
    t = threading.Thread(target = l.runForever)
    t.start()
    l.isRunning = True
    startBackup = True
    with connt:
        queryUpdateAllStatus = "UPDATE computador SET status = 'Na Fila' WHERE heavy = 0 and ignory = 0 "
        cur.execute(queryUpdateAllStatus)
        connt.commit()
    redirect('/')
    

@route('/startfullbackup/<idComputador>')
def startfullbackup(idComputador):
    connt.ping(True)    
    t = TaksBackup()
    f = threading.Thread(target = t.runBackupFull)
    t.idComputador = idComputador
    t.isRunningFull = True
    f.start()
    with connt:
        queryUpdateAllStatus = "UPDATE computador SET status = 'Na Fila' WHERE heavy = 0 "
        cur.execute(queryUpdateAllStatus)
        connt.commit()
    #t.isRunningFull = False    
    redirect('/')
    


@route('/stopbackup')
def stop():
    global startBackup
    global l
    connt.ping(True)
    l.isRunning = False
    startBackup = False
    with connt:
        queryUpdateAllStatus = "UPDATE computador SET status = 'Serviço Parado' WHERE heavy = 0 and ignory = 0 "
        cur.execute(queryUpdateAllStatus)
        connt.commit()
    cmdDir = 'process.bat' #KILL THE PROCESS AND RESTART
    os.system(cmdDir)
    redirect('/')

@route('/novo')
def novo():
    computadores = [('','','','','','','','','')]
    connt.ping(True)
    return template('formcomputer', results = computadores, idCp = "")

@route('/config')
def config():
    queryGlobalSettings = "SELECT * FROM globalsettings"
    with connt:
        cur.execute(queryGlobalSettings)
        config = cur.fetchall()
        if len(config) < 1:
            config = [('','','')]
    return template('formconfig', results = config)

@route('/saveconfig', method='POST')
def saveconfig():
    connt.ping(True)
    intervalIncr = request.forms.get("inputIncr")
    intervalFull = request.forms.get("inputFull")
    queryGlobalSettings = "SELECT * FROM globalsettings"
    with connt:
        cur.execute(queryGlobalSettings)
        count = cur.fetchall()
        if len(count) > 0:
            actGlobalSettings = "UPDATE globalsettings SET interval_full = '%s', interval_incr = '%s'" % (intervalFull, intervalIncr)
        else:
            actGlobalSettings = "INSERT INTO globalsettings (interval_full, interval_incr ) VALUES ('%s', '%s')" % (intervalFull, intervalIncr)
        cur.execute(actGlobalSettings)
        connt.commit()
        redirect('/config')
    

@route('/editar/<idComputador>')
def editar(idComputador):
    connt.ping(True)
    queryEditar = "SELECT * FROM computador WHERE id = %d" %(int(idComputador))
    cur.execute(queryEditar)
    computadores = cur.fetchall()
    return template('formcomputer', results=computadores, idCp = idComputador)



@route('/folders/<idComputador>')
def folders(idComputador):
    connt.ping(True)
    queryFolders = "SELECT cp.id, cp.enderecoPasta ,cp.idComputador, co.name FROM copiarpasta cp INNER JOIN computador co ON co.id = cp.idComputador WHERE idComputador = %d " % (int(idComputador))
    cur.execute(queryFolders)
    folders = cur.fetchall()
    namepc = ""
    cur.execute("SELECT name FROM computador WHERE id= %d " % (int(idComputador)))
    computador = cur.fetchall()
    for c in computador:
        namepc = c[0]
    return template('containerfolders', results=folders, idCp = idComputador, computador = namepc)

@route('/novapasta/<idComputador>')
def novapasta(idComputador):
    pastas = [('','','')]
    cur.execute("SELECT name FROM computador WHERE id= %d" % (int(idComputador)))
    computador = cur.fetchall()
    for c in computador:
        namepc = c[0]
    return template('formpastas', results = pastas, idComputador = idComputador, acao= "Adicionar Pasta", computador = namepc)

@route('/editarpasta/<idPasta>')
def editarpasta(idPasta):    
    cur.execute("SELECT cp.id, cp.enderecoPasta ,cp.idComputador, co.name FROM copiarpasta cp INNER JOIN computador co ON co.id = cp.idComputador WHERE cp.id ="+idPasta+"")
    datapasta = cur.fetchall()
    for d in datapasta:
        namepc = d[3]
        idPc = d[2]
    return template('formpastas', results=datapasta, acao= "Editar Pasta", idFolder = idPasta,idComputador = idPc, computador=namepc)

@route('/apagar/<idComputador>')
def apagar(idComputador):
    queryDeleteFoldersByPc="DELETE  FROM copiarpasta WHERE idComputador=%d" % (int(idComputador))
    queryDeleteComputador = "DELETE FROM computador WHERE id=%d "% (int(idComputador))
    cur.execute(queryDeleteFoldersByPc)
    cur.execute(queryDeleteComputador)
    connt.commit()
    redirect('/')

@route('/logs/<idComputador>')
def logs(idComputador):
    queryLogs = "SELECT c.name, l.mensagem, l.data FROM logs l INNER JOIN computador c ON l.idComputador = c.id  WHERE idComputador = %d ORDER BY l.id DESC LIMIT 1, 300" % (int(idComputador))
    cur.execute(queryLogs)
    logs = cur.fetchall()
    return template('containerlogs', results = logs, acao = "Visualizar Logs")

@route('/apagarpasta/<idPasta>')
def apagarpasta(idPasta):
    cur.execute("SELECT idComputador FROM copiarpasta WHERE id = "+idPasta+"")
    datapc = cur.fetchall()
    for d in datapc:
        idComputador = d[0]
    cur.execute("DELETE FROM copiarpasta WHERE id="+str(idPasta))
    connt.commit()
    totalFiles = size(getDirectoryTotalSize(int(idComputador)))
    updateComputador = "UPDATE computador SET totalSize ='%s' WHERE id = %d" % (totalFiles, int(idComputador))
    cur.execute(updateComputador)
    connt.commit()
    redirect('/folders/'+str(idComputador))


@route('/savefolder', method='POST')
def savefolder():
    idComputador = request.forms.get("idcomputador")    
    pasta = request.forms.get("source")
    pasta = pasta.replace("\\","\\\\")
    idPasta = request.forms.get("idpasta")
    queryExec = ""
    act = ""
    if idPasta == "":
        queryExec = "INSERT INTO copiarpasta (enderecopasta,idComputador) VALUES ('%s',%d)" % (pasta,int(idComputador))           
    else:
        queryExec = "UPDATE copiarpasta SET enderecopasta='%s'  WHERE id=%d" % (pasta,int(idPasta))
        connt.commit()
        act = True
    act = cur.execute(queryExec)
    connt.commit()    
    if act:        
        totalFiles = size(getDirectoryTotalSize(int(idComputador)))
        updateComputador = "UPDATE computador SET totalSize ='%s' WHERE id = %d" % (totalFiles, int(idComputador))
        cur.execute(updateComputador)
        connt.commit()
        redirect("/folders/"+str(idComputador))
   
   

@route('/about')
def about():
    return template("containerabout")

@route("/clickSenderIng", method='POST')
def setComputadorIgnore():
    idComputador = request.forms.get("idComputador")
    checkBoxIgn = request.forms.get("valueFied")
    print idComputador, checkBoxIgn
    queryUpdateIgn = "UPDATE computador SET ignory = %d WHERE id = %d " % (int(checkBoxIgn), int(idComputador))
    cur.execute(queryUpdateIgn)
    connt.commit()

@route('/savecomputer', method='POST')
def savecomputer():
    idComputador = request.forms.get("idcomputador")
    computador = request.forms.get("computador")
    heavy_check = request.forms.get("heavy")
    if idComputador == "":
        idComputador = 0
    if heavy_check == None:
        heavy_check = 0
    else:
        heavy_check = 1
   
    destino = request.forms.get('destino')
    destino = destino.replace("\\","\\\\")

    interval_full = request.forms.get("inputFull")
    interval_incr = request.forms.get("inputIncr")
    
    msg = ""
    queryComputadorInsert = "INSERT INTO computador (name, destino,heavy, interval_full, interval_incr) VALUES ('%s','%s', %d, %d, %d)" % (computador, destino, heavy_check, int(interval_full), int(interval_incr))
    queryComputadorUpdate = "UPDATE computador SET name = '%s', destino= '%s', heavy = %d, interval_full=%d, interval_incr=%d   WHERE id = %d" % (computador, destino,heavy_check,  int(interval_full), int(interval_incr), int(idComputador))   
    
    if idComputador == "" or idComputador == 0:
        act = cur.execute(queryComputadorInsert)            
    else:
        act = cur.execute(queryComputadorUpdate)
    connt.commit()   
    redirect("/")           
   

@route('/error')
def error():
    return template('containererror')

run(host='localhost', port=8180)
