from flask import Flask,render_template,request
import requests
import subprocess
import sqlite3
import random
from apscheduler.schedulers.background import BackgroundScheduler
import json

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
                                        ac_prendido integer
                                    );"""
    cursor.execute(sql_create_temperaturas_table)
    #El aire siempre inicia apagado
    sql_insert_status_ac = """ INSERT INTO status_ac (datetime, ac_prendido)
                               VALUES(datetime('now', 'localtime'),false);
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
def toggle_ac():    
    aire_prendido = status_ac().get('aire_prendido')
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_insert_status_ac = """INSERT INTO status_ac (datetime, ac_prendido)
                               VALUES(datetime('now', 'localtime'),?);"""
    if aire_prendido:
        #Ejecutar comando para apagar aire
        try:
            subprocess.run("ir-ctl -d /dev/lirc0 -s ac_off".split())
        except:
            pass
        aire_prendido = False
    else:
        #Ejecutar comando para prender aire
        try:
            subprocess.run("ir-ctl -d /dev/lirc0 -s ac_on".split())
        except:
            pass
        aire_prendido = True
    cursor.execute(sql_insert_status_ac,[aire_prendido])
    conn.commit()
    conn.close()
    return {'aire_prendido':aire_prendido}

@app.route('/status_ac')
def status_ac():
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_select_temperatura = """ select * from status_ac ORDER BY id desc LIMIT 1;"""
    cursor.execute(sql_select_temperatura)
    rsp = [dict(row) for row in cursor.fetchall()]
    print(rsp)
    conn.close()
    return {'aire_prendido':rsp[0].get("ac_prendido")==1}        

def get_ultima_temperatura():        
    conn = db_get_connection()
    cursor = conn.cursor()
    sql_select_temperatura = """ select * from temperaturas order by id desc LIMIT 1; """
    cursor.execute(sql_select_temperatura)
    rsp = [dict(row) for row in cursor.fetchall()]    
    conn.close()
    return json.dumps(rsp[0].get("temp_celsius"))

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
    #Metemos un numero random como temperatura, reemplazar con lectura del sensor                                                     
    random.seed()
    temperatura = random.randrange(15,25) 
    cursor.execute(sql_insert_temperatura,[temperatura])    
    conn.commit()
    conn.close()
#Inicializa el job de actualizar la temperatura cada x tiempo
sched = BackgroundScheduler()
sched.add_job(update_temperatura, 'interval', seconds =5)
sched.start()
