#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>

Servo myservo;

const char* ssid = "cosmic";
const char* password = "aptx48694062";

HTTPClient client;
DynamicJsonDocument json(1024);

#if defined(CONFIG_IDF_TARGET_ESP32S2) || defined(CONFIG_IDF_TARGET_ESP32S3)
int servoPin = 17;
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
int servoPin = 7;
#else
int servoPin = 18;
#endif

void handle_request();

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);
  myservo.setPeriodHertz(50);
  myservo.attach(servoPin, 1000, 2000);
  
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  client.begin("https://control-servo-c8729-default-rtdb.firebaseio.com/.json");
  client.addHeader("Content-Type", "application/json");
}

void loop() {
  // put your main code here, to run repeatedly:
  handle_request();
}

void handle_request(){
  int http_code = client.GET();

  if(http_code > 0){
    String content = client.getString();
    deserializeJson(json, content);
    int angle = json["angle"];

    myservo.write(angle);
    delay(100);
  }
}
