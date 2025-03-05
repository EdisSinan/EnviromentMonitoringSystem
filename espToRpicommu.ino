#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "pscgrr";
const char* password = "svezadesetku";

// Change the variable to your Raspberry Pi IP address, so it connects to your MQTT broker
const char* mqtt_server = "192.168.40.89";

// Initializes the espClient
WiFiClient espClient;
PubSubClient client(espClient);

int _moisture,sensor_analog;
const int sensor_pin = A0;  /* Soil moisture sensor O/P pin */
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}

void setup(void){
  Serial.begin(9600);     /* Set the baudrate to 115200*/
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  
  Serial.println();
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");  
      client.subscribe("esp32/4");
      client.subscribe("esp32/5");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(15000);
    }
  }
}


void loop(void){
   if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
    client.connect("ESP8266Client");
  sensor_analog = analogRead(sensor_pin);
  _moisture = ( 100 - ( (sensor_analog/4095.00) * 100 ) );
    //float hic = dht.computeHeatIndex(t, h, false);
    static char MOS[7];
    dtostrf(_moisture, 6, 2,MOS );
  Serial.print("Moisture = ");
  Serial.print(_moisture);  /* Print Temperature on the serial window */
  Serial.println("%");
  Serial.print(MOS);
  client.publish("/esp32/light", MOS);
  delay(1000);              /* Wait for 1000mS */
}
