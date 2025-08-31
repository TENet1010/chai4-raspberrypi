import json
import time
import paho.mqtt.client as mqtt
import lgpio

# MQTT config
MQTT_BROKER = "172.20.10.5"  # IP ของ Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/rotary_ultrasonic"

# GPIO setup with lgpio
h = lgpio.gpiochip_open(0)

# Rotary encoder pins
CLK = 17
DT = 27
SW = 22

# Ultrasonic pins
TRIG = 26
ECHO = 19

# Setup GPIO pins
lgpio.gpio_claim_input(h, CLK, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(h, DT, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(h, SW, lgpio.SET_PULL_UP)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

# MQTT client
client = mqtt.Client(client_id="rasp_pi_5")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Rotary variables
last_clk = lgpio.gpio_read(h, CLK)
rotary_counter = 0

def read_ultrasonic():
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.05)
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)
    
    pulse_start, pulse_end = time.time(), time.time()
    
    # Wait for echo start
    while lgpio.gpio_read(h, ECHO) == 0:
        pulse_start = time.time()
    
    # Wait for echo end
    while lgpio.gpio_read(h, ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  # cm
    return round(distance, 2)

try:
    while True:
        # --- Rotary ---
        clk_state = lgpio.gpio_read(h, CLK)
        dt_state = lgpio.gpio_read(h, DT)
        
        if clk_state != last_clk:
            if dt_state != clk_state:
                rotary_counter += 1
            else:
                rotary_counter -= 1
        last_clk = clk_state
        
        # --- Ultrasonic ---
        distance = read_ultrasonic()
        
        # --- Publish MQTT ---
        payload = json.dumps({
            "rotary": rotary_counter,
            "ultrasonic_cm": distance
        })
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        
        time.sleep(1)

except KeyboardInterrupt:
    lgpio.gpiochip_close(h)