from gpiozero import Button, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import paho.mqtt.client as mqtt
import json

# ======================
# MQTT configuration
# ======================
MQTT_BROKER = "172.20.10.3"  # IP ของ ESP32 หรือ broker กลาง
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/rotary_ultrasonic"

# ======================
# Pigpio factory (ต้อง run pigpiod service)
# ======================
factory = PiGPIOFactory()

# ======================
# Sensors setup
# ======================
# Rotary switch (ปุ่มกดของ rotary encoder)
rotary_sw = Button(22, pin_factory=factory)

# Ultrasonic sensor
sensor = DistanceSensor(echo=19, trigger=26, pin_factory=factory)

# ======================
# MQTT client setup
# ======================
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# ======================
# Variables
# ======================
rotary_counter = 0

# ======================
# Main loop
# ======================
try:
    while True:
        # อ่าน rotary switch
        if rotary_sw.is_pressed:
            rotary_counter += 1  # เพิ่มค่าเมื่อปุ่มกด

        # อ่าน ultrasonic (ระยะเป็น cm)
        distance = sensor.distance * 100  # sensor.distance ให้ค่าเป็นเมตร

        # สร้าง payload JSON
        payload = json.dumps({
            "rotary": rotary_counter,
            "ultrasonic_cm": round(distance, 2)
        })

        # ส่งค่าไป MQTT
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

        sleep(1)  # หน่วง 1 วินาที

except KeyboardInterrupt:
    print("Exit program")
