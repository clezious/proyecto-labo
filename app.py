from flask import Flask,render_template,request
import requests
import subprocess
import sqlite3
import random
from apscheduler.schedulers.background import BackgroundScheduler
import json

try:
    from w1thermsensor import W1ThermSensor
except:
    #Para desarrollo
    pass

app = Flask(__name__)

def db_get_connection():
    try:
        conn = sqlite3.connect('temperaturas.db')
        conn.row_factory = sqlite3.Row
    except Error as e:
        print(e)
    return conn

def init_sqlite3():
    """Inicializa la base de datos y tabla de temperaturas y status_ac"""
    conn = sqlite3.connect('temperaturas.db')
    cursor = conn.cursor()
    sql_create_temperaturas_table = """ CREATE TABLE IF NOT EXISTS temperaturas (
                                        id integer PRIMARY KEY,                                        
                                        datetime text,
                                        temp_celsius real
                                    ); """
    cursor.execute(sql_create_temperaturas_table)                                
    sql_create_temperaturas_table = """ CREATE TABLE IF NOT EXISTS status_ac (
                                        id integer PRIMARY KEY,                                        
                                        datetime text,
                                        aire_encendido integer,
                                        modo_automatico_encendido integer,
                                        temp_encendido real,
                                        temp_apagado real
                                    );"""
    cursor.execute(sql_create_temperaturas_table)
    #El aire siempre inicia apagado
    sql_insert_status_ac = """ INSERT INTO status_ac (datetime, aire_encendido,modo_automatico_encendido,temp_encendido,temp_apagado)
                               VALUES(datetime('now', 'localtime'),false,false,24,23);
                           """  
    cursor.execute(sql_insert_status_ac)
    conn.commit()
    conn.close()
#Inicializa db
init_sqlite3()

@app.route('/')
def index():
    return render_template('index.html',temperatura=get_ultima_temperatura())

@app.route('/toggle_ac')
def toggle_ac(manual=True):    
    status = status_ac()
    aire_encendido = status.get('aire_encendido')

    conn = db_get_connection()
    cursor = conn.cursor()
    sql_insert_status_ac = """INSERT INTO status_ac (datetime, aire_encendido,modo_automatico_encendido,temp_encendido,temp_apagado)
                               VALUES(datetime('now', 'localtime'),?,?,?,?);"""
    if aire_encendido:
        #Ejecutar comando para apagar aire
        try:
            subprocess.run("ir-ctl -d /dev/lirc0 -s ac_off".split())
        except:
            pass
        aire_encendido = False
    else:
        #Ejecutar comando para prender aire
        try:
            subprocess.run("ir-ctl -d /dev/lirc0 -s ac_on".split())
        except:
            pass
        aire_encendido = True
    #Si el toggle se realizó de forma manual, se desactiva el modo automatico
    if manual:
        status["modo_automatico_encendido"] = 0
    #Se inserta una nueva fila con el status anterior pero con el aire encendido/apagado segun corresponda
    cursor.execute(sql_insert_status_ac,[aire_encendido,status.get('modo_automatico_encendido'),status.get('temp_encendido'),status.get('temp_apagado')])
    conn.commit()
    conn.close()
    return status_ac()

@app.route('/update_modo_automatico_ac',methods=['GET','POST'])
def update_modo_automatico_ac():
    req = request.get_json()
    status = status_ac()
    modo_automatico_encendido = status.get('modo_automatico_encendido')
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_insert_status_ac = """INSERT INTO status_ac (datetime, aire_encendido,modo_automatico_encendido,temp_encendido,temp_apagado)
                               VALUES(datetime('now', 'localtime'),?,?,?,?);"""
    
    #Solo cambia el estado del modo automatico si se recibe el parametro toggle = True
    if req.get("toggle"):
        if modo_automatico_encendido:
            modo_automatico_encendido = False
        else:
            modo_automatico_encendido = True
    #Se inserta una nueva fila con el status anterior pero con el modo automatico encendido/apagado segun corresponda
    cursor.execute(sql_insert_status_ac,[status.get('aire_encendido'),modo_automatico_encendido,req.get('temp_encendido'),req.get('temp_apagado')])
    conn.commit()
    conn.close()
    return status_ac()

def check_modo_automatico():
    #Si se encuentra activo el modo automatico, entonces hace los chequeos 
    #de temperatura correspondientes y activa o desactiva el aire acondicionado.
    status = status_ac()
    temperatura_actual = get_ultima_temperatura()    
    if status.get('modo_automatico_encendido'):
        if (status.get('temp_apagado') >= temperatura_actual and status.get("aire_encendido")) or (status.get('temp_encendido') <= temperatura_actual and not status.get("aire_encendido")):            
            toggle_ac(manual=False)

@app.route('/status_ac')
def status_ac():
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_select_status_ac = """ select * from status_ac ORDER BY id desc LIMIT 1;"""
    cursor.execute(sql_select_status_ac)
    rsp = [dict(row) for row in cursor.fetchall()]
    print(rsp)
    conn.close()         
    return rsp[0]

def get_ultima_temperatura():        
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_select_temperatura = """ select * from temperaturas order by id desc LIMIT 1; """
    cursor.execute(sql_select_temperatura)
    rsp = [dict(row) for row in cursor.fetchall()]    
    conn.close()
    return rsp[0].get("temp_celsius")

@app.route('/get_temperaturas')
def get_temperaturas(limite=20):        
    conn = db_get_connection()   
    cursor = conn.cursor()
    sql_select_temperatura = """ select * from temperaturas order by id desc LIMIT ?; """
    cursor.execute(sql_select_temperatura,[limite])
    rsp = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(rsp)

def update_temperatura():
    conn = sqlite3.connect('temperaturas.db')
    cursor = conn.cursor()
    sql_insert_temperatura = """ INSERT INTO temperaturas (datetime, temp_celsius)
                                 VALUES(datetime('now', 'localtime'),?);
                            """           
    #Obtenemos la lectura del sensor
    try:                                               
        sensor = W1ThermSensor()
        temperatura = sensor.get_temperature()
    except:
        #Para debug en desarrollo si no obtenemos nada del sensor, generamos un random alto. Quitar.
        random.seed()
        temperatura = random.randrange(60,80)
    cursor.execute(sql_insert_temperatura,[temperatura])    
    conn.commit()
    conn.close()

#Jobs    
sched = BackgroundScheduler()
#Inicializa el job de actualizar la temperatura cada x tiempo
sched.add_job(update_temperatura, 'interval', seconds =5)
#Inicializa el job de chequear modo automatico cada x tiempo
sched.add_job(check_modo_automatico, 'interval', seconds =5)
sched.start()
