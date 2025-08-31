import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json

# MQTT setup
MQTT_BROKER = "172.20.10.3"  # ใส่ IP ESP32 หรือ broker กลาง
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/rotary_ultrasonic"

# Rotary encoder pins
CLK = 17
DT = 27
SW = 22

# Ultrasonic pins
TRIG = 26
ECHO = 19

GPIO.setmode(GPIO.BCM)

# Rotary setup
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ultrasonic setup
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Rotary variables
last_clk = GPIO.input(CLK)
rotary_counter = 0

def read_ultrasonic():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  # cm
    return round(distance, 2)

try:
    while True:
        # --- อ่าน Rotary ---
        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)
        sw_state = GPIO.input(SW)

        if clk_state != last_clk:
            if dt_state != clk_state:
                rotary_counter += 1
            else:
                rotary_counter -= 1
        last_clk = clk_state

        # --- อ่าน Ultrasonic ---
        distance = read_ultrasonic()

        # --- ส่ง MQTT เป็น JSON ---
        payload = json.dumps({
            "rotary": rotary_counter,
            "ultrasonic_cm": distance
        })
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
