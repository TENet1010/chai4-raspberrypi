from gpiozero import Button, DistanceSensor
from time import sleep
import paho.mqtt.client as mqtt
import json

# MQTT configuration
MQTT_BROKER = "172.20.10.3"  # IP ESP32 หรือ broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/rotary_ultrasonic"

# Sensors setup (gpiozero default, ใช้ RPi.GPIO backend)
rotary_sw = Button(22)  # ปุ่มกดของ rotary encoder
ultrasonic = DistanceSensor(echo=19, trigger=26)  # ระยะเป็นเมตร

# MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Variables
rotary_counter = 0

# Main loop
try:
    while True:
        # อ่าน rotary
        if rotary_sw.is_pressed:
            rotary_counter += 1

        # อ่าน ultrasonic
        distance_cm = round(ultrasonic.distance * 100, 2)  # แปลงเป็น cm

        # ส่ง JSON ผ่าน MQTT
        payload = json.dumps({
            "rotary": rotary_counter,
            "ultrasonic_cm": distance_cm
        })

        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

        sleep(1)

except KeyboardInterrupt:
    print("Exiting program")
