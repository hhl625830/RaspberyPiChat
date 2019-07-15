#include <Wire.h>
#include <Servo.h>
#include <PID_v1.h>

#define SLAVE_ADDRESS 0x04

#define NUM_DATA 2
byte data[NUM_DATA];
byte cur_data_index;
byte state;
Servo servoNeckX;
Servo servoNeckY;

const byte servoNeckX_pin = 3;
const byte servoNeckY_pin = 4;

// Servo Angle constrains (Good Practice! :)
const int lrServoMax = 2100; // looking right
const int lrServoMin = 700;
const int udServoMax = 2100; // looking down
const int udServoMin = 750; // looking up

// Init Servo Position
int posX = 1550;
int posY = 1600;

// — Init PID Controller —

//Define Variables we’ll be connecting to
double SetpointX, InputX, OutputX;
double SetpointY, InputY, OutputY;

//Specify the links and initial tuning parameters
// face tracking: 0.8, 0.6, 0
// color tracking: 0.4, 0.4, 0
//PID myPIDX(&InputX, &OutputX, &SetpointX, 0.4, 0.4, 0, DIRECT);
//PID myPIDY(&InputY, &OutputY, &SetpointY, 0.4, 0.4, 0, DIRECT);
PID myPIDX(&InputX, &OutputX, &SetpointX, 0.8, 0, 0, DIRECT);
PID myPIDY(&InputY, &OutputY, &SetpointY, 0.5, 0, 0, DIRECT);
void setup() {
  // put your setup code here, to run once:
  // — I2C Setup —
  
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  // — Setup PID —

  SetpointX = 100;
  SetpointY = 100;
  myPIDX.SetOutputLimits(-255, 255);
  myPIDY.SetOutputLimits(-255, 255);

  //turn PIDs on
  myPIDX.SetMode(AUTOMATIC);
  myPIDY.SetMode(AUTOMATIC);

  // — Setup Servos —

  servoNeckX.attach(servoNeckX_pin);
  servoNeckX.writeMicroseconds(posX);

  servoNeckY.attach(servoNeckY_pin);
  servoNeckY.writeMicroseconds(posY);

  state = 1;
  cur_data_index = 0;

  Serial.begin(9600); // start serial for output
  Serial.println("Ready");
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(20);
}

// callback for received data
void receiveData(int byteCount) {

  // Update Slave Status – Occupied
  state = 0;

  while (Wire.available()) {

    data[cur_data_index++] = Wire.read();

    // When we have received both X and Y coordinates
    if (cur_data_index >= NUM_DATA) {
      cur_data_index = 0;

      // Calculate PID outputs with Inputs
      InputX = data[0];
      InputY = data[1];
      Serial.println(InputX);
      Serial.println(InputY);
      myPIDX.Compute();
      myPIDY.Compute();
      // Update Servo Position
      posX = constrain(posX + OutputX, lrServoMin, lrServoMax);
      posY = constrain(posY + OutputY, udServoMin, udServoMax);
      servoNeckX.writeMicroseconds(posX);
      servoNeckY.writeMicroseconds(posY);

      // Update Slave Status – Available
      state = 1;
    }

  }
}

// callback for sending data
void sendData() {
  Wire.write(state);
}
