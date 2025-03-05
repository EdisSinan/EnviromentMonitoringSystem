import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_tcs34725
import requests
import csv
from MLX90614 import *

# GPIO setup
RELAY_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initialize the relay as off (assuming active-low relay)

# GPIO setup for servo motor
SERVO_PIN = 25
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Create I2C instance
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor2 = MLX90614()

# Flag to control MQTT message processing
process_mqtt_messages = True

# State variables
relay_state = "OFF"
servo_state = "OFF"
mqtt_value = 0

# CSV file setup
csv_file = "sensor_data.csv"
csv_header = ["timestamp", "red", "green", "blue", "object_temperature", "ambient_temperature", "relay_state", "servo_state", "mqtt_value"]

# Create and write header to CSV file if it doesn't exist
with open(csv_file, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

def send_to_flask(data):
    url = 'http://localhost:5000/data'
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"Failed to send data to Flask server: {e}")

def save_to_csv(data):
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data.values())

# Callback for when the client receives a connection acknowledgment from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/esp32/light")

# Callback for when a PUBLISH message is received from the server
def on_message(client, userdata, message):
    global process_mqtt_messages, relay_state, mqtt_value
    if not process_mqtt_messages:
        return

    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")
    
    try:
        mqtt_value = float(message.payload.decode().strip())
        if mqtt_value < 87:
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn on the relay (active-low)
            relay_state = "ON"
            msg = "Relay turned ON (active-low)"
            print(msg)
            send_to_flask({"timestamp": time.ctime(), "message": msg})
        else:
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn off the relay (active-low)
            relay_state = "OFF"
            msg = "Relay turned OFF (active-low)"
            print(msg)
            send_to_flask({"timestamp": time.ctime(), "message": msg})
    except ValueError:
        msg = "Received non-numeric value"
        print(msg)
        send_to_flask({"timestamp": time.ctime(), "message": msg})

def main():
    global process_mqtt_messages, relay_state, servo_state, mqtt_value

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect('localhost', 1883, 60)

    mqtt_client.loop_start()
    
    try:
        while True:
            color_rgb = sensor.color_rgb_bytes
            red, green, blue = color_rgb
            temperature = sensor2.readObjectTemperature()
            ambijent = sensor2.readAmbientTemperature()
            process_mqtt_messages = True
            print("Object:", sensor2.readObjectTemperature())
            print("Ambient:", sensor2.readAmbientTemperature())
            print(f"Sensor RGB values: Red: {red}, Green: {green}, Blue: {blue}")

            data = {
                "timestamp": time.ctime(),
                "red": red,
                "green": green,
                "blue": blue,
                "object_temperature": temperature,
                "ambient_temperature": ambijent,
                "relay_state": relay_state,
                "servo_state": servo_state,
                "mqtt_value": mqtt_value,
                "message": "Sensor values updated"
            }
            send_to_flask(data)
            save_to_csv(data)

            if green > red + 10 and green > blue + 10:
                servo_state = "OFF"
                msg = "Green value is greater by at least 10."
                print(msg)
                send_to_flask({"timestamp": time.ctime(), "message": msg})
                pwm.ChangeDutyCycle(0)  # Activate servo motor
            else:
                servo_state = "ON"
                msg = "Green value is not greater by at least 10. Running servo motor for 5 seconds."
                print(msg)
                send_to_flask({"timestamp": time.ctime(), "message": msg})
                process_mqtt_messages = False  # Pause MQTT message processing

                pwm.ChangeDutyCycle(5)  # Activate servo motor
                time.sleep(5)  # Run servo for 5 seconds
                pwm.ChangeDutyCycle(0)  # Deactivate servo motor

                msg = "Turning relay on for 3 seconds."
                print(msg)
                send_to_flask({"timestamp": time.ctime(), "message": msg})
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn on the relay (active-low)
                relay_state = "ON"
                time.sleep(1.5)  # Relay on for 3 seconds
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn off the relay (active-low)
                relay_state = "OFF"

                process_mqtt_messages = True  # Resume MQTT message processing

            if temperature > 28:
                msg = "The temperature of the terrain is too high. Watering the terrain."
                print(msg)
                send_to_flask({"timestamp": time.ctime(), "message": msg})
                process_mqtt_messages = False 
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn on the relay (active-low)
                relay_state = "ON"
                time.sleep(5)  # Relay on for 5 seconds
                process_mqtt_messages = True
            else:
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn off the relay (active-low)
                relay_state = "OFF"

            time.sleep(5)

    except KeyboardInterrupt:
        print("Disconnecting from broker")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
