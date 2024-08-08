/*
  limit = 255mm
  lead: 30mm
  min_interval = 700
*/
#define INTERVAL 700 // [us]
#define BAUDRATE 115200

struct stepmotor {
  uint8_t ENA;
  uint8_t DIR;
  uint8_t PUL;
};

stepmotor stm = {2, 3, 4};
String str;
int16_t num;

void setup() {
  Serial.begin(BAUDRATE);

  pinMode(stm.ENA, OUTPUT);
  pinMode(stm.DIR, OUTPUT);
  pinMode(stm.PUL, OUTPUT);
  
  digitalWrite(stm.ENA, LOW);
  digitalWrite(stm.DIR, LOW);
  digitalWrite(stm.PUL, LOW);

  Serial.println("Set done");
}

void loop() {
  if (Serial.available()) {
    Serial.println("-----------------");
    str = Serial.readString();
    num = str.toInt();
    Serial.print("Input pulse: ");
    Serial.println(num);

    if(num < 0) {
      digitalWrite(stm.DIR, HIGH);
      for (int16_t i = 0; i < -num; i++) {
        digitalWrite(stm.PUL, HIGH);
        delayMicroseconds(INTERVAL);
        digitalWrite(stm.PUL, LOW);
        delayMicroseconds(INTERVAL);
      }
    } else {
      digitalWrite(stm.DIR, LOW);
      for (int16_t i = 0; i < num; i++) {
        digitalWrite(stm.PUL, HIGH);
        delayMicroseconds(INTERVAL);
        digitalWrite(stm.PUL, LOW);
        delayMicroseconds(INTERVAL);
      }
    }
    Serial.println("done");
  }
}
