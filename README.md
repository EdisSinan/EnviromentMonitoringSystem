# Smart Environment Monitoring and Control System

This project is a smart environment monitoring and control system that uses a Raspberry Pi to interact with various sensors and actuators. The system collects data from a color sensor (TCS34725) and an infrared temperature sensor (MLX90614), controls a relay and a servo motor based on the sensor data, and communicates with an MQTT broker to receive additional control commands. The collected data is logged to a CSV file and sent to a Flask server for further processing or visualization.

## Features

- **Color Sensing**: The system uses the TCS34725 color sensor to detect RGB values from the environment.
- **Temperature Sensing**: The MLX90614 infrared temperature sensor measures both object and ambient temperatures.
- **Relay Control**: A relay is controlled based on MQTT messages and temperature thresholds.
- **Servo Motor Control**: A servo motor is activated based on the color sensor's green value.
- **Data Logging**: Sensor data and system states are logged to a CSV file.
- **Flask Integration**: Data is sent to a Flask server for real-time monitoring or further processing.
- **MQTT Communication**: The system subscribes to an MQTT topic to receive control commands.

## Hardware Requirements

- Raspberry Pi (with GPIO pins)
- ESP8266
- TCS34725 Color Sensor
- MLX90614 Infrared Temperature Sensor
- Relay Module
- Servo Motor
- Jumper Wires
- Breadboard (optional)

## Software Requirements

- Python 3.x
- Libraries:
  - `paho-mqtt`
  - `RPi.GPIO`
  - `adafruit_tcs34725`
  - `MLX90614`
  - `requests`
  - `csv`
  - `time`
  - `busio`
  - `board`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/smart-environment-monitoring.git
   cd smart-environment-monitoring
   ```

2. **Install Required Libraries**:
   ```bash
   pip install paho-mqtt RPi.GPIO adafruit-circuitpython-tcs34725 requests
   ```

3. **Set Up the Hardware**:
   - Connect the TCS34725 and MLX90614 sensors to the Raspberry Pi's I2C pins.
   - Connect the relay module to GPIO pin 21.
   - Connect the servo motor to GPIO pin 25.

4. **Run the Script**:
   ```bash
   python main.py
   ```

## Code Overview

### GPIO Setup
The script initializes the GPIO pins for the relay and servo motor. The relay is set to be active-low, meaning it turns on when the GPIO pin is LOW.

### I2C Setup
The I2C bus is initialized to communicate with the TCS34725 color sensor and the MLX90614 temperature sensor.

### MQTT Setup
The script connects to an MQTT broker and subscribes to the `/esp32/light` topic. Messages received on this topic control the relay based on the received value.

### Main Loop
The main loop continuously reads data from the sensors, logs it to a CSV file, and sends it to a Flask server. The system also controls the relay and servo motor based on the sensor data and MQTT messages.

### Functions
- **`send_to_flask(data)`**: Sends sensor data to a Flask server.
- **`save_to_csv(data)`**: Logs sensor data to a CSV file.
- **`on_connect(client, userdata, flags, rc)`**: Callback for MQTT connection.
- **`on_message(client, userdata, message)`**: Callback for handling MQTT messages.
- **`main()`**: The main function that initializes the system and runs the main loop.

## Usage

1. **Start the Flask Server**:
   Ensure that the Flask server is running and accessible at `http://localhost:5000`.

2. **Run the Script**:
   Execute the script on the Raspberry Pi. The system will start collecting data and controlling the relay and servo motor based on the sensor readings and MQTT messages.

3. **Monitor Data**:
   The collected data will be logged to `sensor_data.csv` and sent to the Flask server for real-time monitoring.

## Example Data Log

The CSV file will contain the following columns:

- `timestamp`: The time when the data was recorded.
- `red`: The red value from the color sensor.
- `green`: The green value from the color sensor.
- `blue`: The blue value from the color sensor.
- `object_temperature`: The temperature of the object measured by the MLX90614 sensor.
- `ambient_temperature`: The ambient temperature measured by the MLX90614 sensor.
- `relay_state`: The current state of the relay (ON/OFF).
- `servo_state`: The current state of the servo motor (ON/OFF).
- `mqtt_value`: The last received MQTT value.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to Adafruit for the TCS34725 library.
- Thanks to the developers of the MLX90614 library.
- Thanks to the Paho MQTT team for the MQTT client library.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or support, please contact [Your Name] at [your.email@example.com].

---

This README provides a comprehensive overview of the project, including installation instructions, usage, and a description of the code. Feel free to customize it further to suit your needs!
