import RPi.GPIO as GPIO
import time

# กำหนดขา
CLK = 17
DT = 27
SW = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_state = GPIO.input(CLK)
counter = 0

try:
    while True:
        clk_state = GPIO.input(CLK)
        dt_state = GPIO.input(DT)
        sw_state = GPIO.input(SW)

        # ตรวจจับการหมุน
        if clk_state != last_state:
            if dt_state != clk_state:
                counter += 1
                print("Clockwise → counter =", counter)
            else:
                counter -= 1
                print("Counterclockwise → counter =", counter)

        last_state = clk_state

        # ตรวจจับปุ่มกด
        if sw_state == 0:
            print("Button Pressed")
            time.sleep(0.3)  # debounce

except KeyboardInterrupt:
    GPIO.cleanup()
