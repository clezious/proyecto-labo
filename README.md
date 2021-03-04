# proyecto-labo
Proyecto Laboratorio FIUBA. Aplicación web para sensar temperatura ambiente con una raspberry pi y controlar el prendido y apagado de un aire acondicionado de forma manual o automática.

Para iniciar la app: 
  python -m flask run --host=0.0.0.0
  
Componentes utilizados:
<ul>
  <li><a href="https://www.pololu.com/product/2750">Raspberry Pi Model B Revision 2</a> (Pueden utilizarse modelos más recientes)</li>
  <li><a href="https://arduinomodules.info/ky-022-infrared-receiver-module/"> Receptor Infrarojo KY-022</a></li>
  <li><a href="https://arduinomodules.info/ky-005-infrared-transmitter-sensor-module/"> Emisor Infrarojo KY-005</a></li>
  <li><a href="https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf"> Sensor de Temperatura ds18b20</a></li>
  <li>Resistencia de 4.7kOhm</li>
  <li>Placa de pruebas</li>
</ul>

Diagrama Conceptual:<br>
![Diagrama Bloques](https://user-images.githubusercontent.com/40214601/109993977-9db55e80-7ceb-11eb-82d5-2904c614c961.png)



Diagramas de conexiones (Los pin realmente utilizados pueden variar):<br>

Sensor de Temperatura:<br>
![sensor_temp](https://user-images.githubusercontent.com/40214601/109988808-a8212980-7ce6-11eb-9a7f-1696dfb7cf96.png)

Emisor Infrarojo:<br>
![ir_sender_bb](https://user-images.githubusercontent.com/40214601/109990338-10243f80-7ce8-11eb-8f40-fbfb53fef76a.jpg)

Receptor Infrarojo:<br>
![ir_receiver_bb](https://user-images.githubusercontent.com/40214601/109990376-187c7a80-7ce8-11eb-9d99-b00c20d88032.jpg)


El Receptor Infrarojo se utiliza de forma auxiliar, solo para obtener los códigos del control remoto real del aparato que se quiere controlar (Si estos estan disponibles de antemano, entonces el receptor no es necesario).




