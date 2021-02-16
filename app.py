from flask import Flask,render_template
import requests
import subprocess

app = Flask(__name__)

AIRE_PRENDIDO = False

@app.route('/')
def index():
    return render_template('index.html',temperatura=get_temperatura())

def get_temperatura():    
    return 22

@app.route('/toggle_ac')
def toggle_ac():
    global AIRE_PRENDIDO
    if AIRE_PRENDIDO:
        #Ejecutar comando para apagar aire
        #subprocess.run("ls -a", shell=True)
        AIRE_PRENDIDO = False
    else:
        #Ejecutar comando para prender aire
        #subprocess.run("ls -a", shell=True)
        AIRE_PRENDIDO = True
    return {'aire_prendido':AIRE_PRENDIDO}
