import json
import time
import random  # ใช้จำลองค่าจาก sensor
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db

# ==== CONFIG ====
MQTT_BROKER = "172.20.10.3"        # IP ของ ESP32 หรือ broker
MQTT_PORT   = 1883
MQTT_TOPIC  = "sensor/rotary_ultrasonic"

FIREBASE_CRED_PATH = "/home/chai4/keys/serviceAccountKey.json"
FIREBASE_DB_URL   = "https://iotjengjeng-20793-default-rtdb.asia-southeast1.firebasedatabase.app/"
DEVICE_ID = "rasp_pi_5"
# =================

# Init Firebase
cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred, {
    "databaseURL": FIREBASE_DB_URL
})

# Realtime DB references
base_ref    = db.reference(f"devices/{DEVICE_ID}")
last_ref    = base_ref.child("last")
history_ref = base_ref.child("history")

def utc_iso():
    return datetime.now(timezone.utc).isoformat()

# MQTT client
client = mqtt.Client(client_id="rasp_pi_5")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

rotary_counter = 0

try:
    while True:
        # --- Simulate sensor values ---
        rotary_counter += random.choice([-1, 0, 1])   # ปรับ rotary ขึ้นลง
        ultrasonic_cm = round(random.uniform(5, 100), 2)  # ระยะ 5-100 cm

        # --- ส่ง MQTT ---
        payload = {
            "rotary": rotary_counter,
            "ultrasonic_cm": ultrasonic_cm,
            "ts_unix": time.time(),
            "ts_iso": utc_iso()
        }
        payload_json = json.dumps(payload)
        client.publish(MQTT_TOPIC, payload_json)
        print(f"Published: {payload_json}")

        # --- เขียน Firebase ---
        last_ref.set(payload)
        history_ref.push(payload)

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program")
