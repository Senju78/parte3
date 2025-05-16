ccconst int ldrPin = A0;
const int leds[] = {2, 3, 4, 5, 6};  // Ajusta los pines si usas otros
const int numLeds = sizeof(leds) / sizeof(leds[0]);

void setup() {
  Serial.begin(9600);

  // Inicializar pines de los LEDs como salida
  for (int i = 0; i < numLeds; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }
}

void loop() {
  // Leer y mandar el valor del LDR
  int valorLuz = analogRead(ldrPin);
  Serial.println(valorLuz);

  // Verificar si hay comandos desde Python
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') {
      // Encender todos los LEDs
      for (int i = 0; i < numLeds; i++) {
        digitalWrite(leds[i], HIGH);
      }
    } else if (comando == '0') {
      // Apagar todos los LEDs
      for (int i = 0; i < numLeds; i++) {
        digitalWrite(leds[i], LOW);
      }
    }
  }

  delay(300);  // Tiempo entre lecturas (coincide con Python)
}
