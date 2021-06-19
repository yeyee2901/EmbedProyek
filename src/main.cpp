#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <LiquidCrystal_I2C.h>
#include <ADS1X15.h>
#include <Adafruit_INA219.h>


#define SSID "THERESIA DWI SUHADI"
#define PASSWORD "GABRIELS"

// #define SSID "Yulius"
// #define PASSWORD "16072000"


// GLOBAL VARS
WiFiClient SocketClient;
float max_voltage;
char max_volt_char[10];
float SHUNT = 0.1;   // nilai resistor kapur
int sample_interval = 100;  // ambil data setiap 100 ms
float elapsed_time = 1;
int count = 0;
int selected_channel = 1;
bool change_channel = false;


ADS1115 ADS(0x48);
LiquidCrystal_I2C lcd(PCF8574_ADDR_A21_A11_A01, 4, 5, 6, 16, 11, 12, 13, 14, POSITIVE);
Adafruit_INA219 ina219;
volatile int buttonpress = 0 ;

IRAM_ATTR void buttoninterrupt(){
    buttonpress++;
}

void setup() {

  Serial.begin(9600);

  // interrupt untuk deteksi button
  pinMode(D5,INPUT);
  attachInterrupt(digitalPinToInterrupt(D5),buttoninterrupt,FALLING);

  // init LCD
  while (lcd.begin(20, 4) != 1) //colums - 20, rows - 4
  {
    Serial.println("Error LCD");
    delay(500);   
  }
  
  // init ADS
  ADS.begin();
  ADS.setGain(0);
  max_voltage = ADS.getMaxVoltage();
  sprintf(max_volt_char, "%.3f", max_voltage);

  lcd.setCursor(0,0);
  lcd.print("Hello World");
  pinMode(LED_BUILTIN,OUTPUT);

  pinMode(LED_BUILTIN,OUTPUT);


  // Connect Wifi   
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID,PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);

  }
  
  String IP = WiFi.localIP().toString();
  lcd.setCursor(0,3);
  lcd.print(IP);

  //cetak max voltage
  lcd.setCursor(0,2);
  lcd.print("Vmax: ");
  lcd.print(max_voltage);
  lcd.print("V");
  delay(2000) ;

  // connect socket PC 
  const char *Laptop_IP = "192.168.1.5";
  int Laptop_PORT = 6969;

  // coba terus sampe sukses
  if( !SocketClient.connect(Laptop_IP, Laptop_PORT) ){
    ;
  }


}



int16_t differential_raw;
float differential_voltage;
float arus;
int16_t val_1;
float tegangan1;
float power;
float konsumsi_energiListrik;

void loop() {

  if(change_channel)
  {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Channel diganti ke:");
    lcd.setCursor(0,1);
    lcd.print(selected_channel);

    change_channel = false;
    delay(3000);
  }

  if (buttonpress > 0)
  {
    lcd.setCursor(0,2);
    lcd.print("                    ");
    lcd.setCursor(0,2);
    lcd.print("button press: ");
    buttonpress=0;
    delay(500);
    lcd.setCursor(0,2);
    lcd.print("                    ");
    SocketClient.stop();
    /* code */
  }
  
  // AMBIL DATA ----------------------------------------------------
  if(selected_channel == 1)
  {
    // differential mode untuk mengukur beda tegangan di resistor shunt
    // arus = beda tegangan / nilai resistor
    differential_raw = ADS.readADC_Differential_0_1();
    differential_voltage = 1000 * ADS.toVoltage(differential_raw);
    arus= differential_voltage / SHUNT ;

    // baca channel 1 untuk ukur tegangan
    val_1 = ADS.readADC(1);
    tegangan1 = ADS.toVoltage(val_1);

    // menghitung daya (power)
    power = arus * tegangan1;

    // menghitung konsumsi daya listrik
    elapsed_time = (( elapsed_time + sample_interval*count) / 1000)  / 3600;
    konsumsi_energiListrik = (power * elapsed_time); // Wh
    konsumsi_energiListrik /= 1000;   // kWh
  }

  else{
    // differential mode untuk mengukur beda tegangan di resistor shunt
    // arus = beda tegangan / nilai resistor
    differential_raw = ADS.readADC_Differential_2_3();
    differential_voltage = 1000 * ADS.toVoltage(differential_raw);
    arus= differential_voltage / SHUNT ;

    // baca channel 1 untuk ukur tegangan
    val_1 = ADS.readADC(3);
    tegangan1 = ADS.toVoltage(val_1);

    // menghitung daya (power)
    power = arus * tegangan1;

    // menghitung konsumsi daya listrik
    elapsed_time = (( elapsed_time + sample_interval*count) / 1000)  / 3600;
    konsumsi_energiListrik = (power * elapsed_time); // Wh
    konsumsi_energiListrik /= 1000;   // kWh
  }


  // konversi ke string --------------------------------------------
  char arus_char_1[5];
  sprintf(arus_char_1, "%.3f", arus);
  
  char differential_char[10];
  sprintf(differential_char, "%.3f", differential_voltage);

  char tegangan1_char[10];
  sprintf(tegangan1_char, "%.3f", tegangan1);

  char power1_char[10];
  sprintf(power1_char, "%.3f", power);

  char energi[10];
  sprintf(energi, "%.6f", konsumsi_energiListrik);


  // menampilkan di LCD ---------------------------------------------
  lcd.setCursor(0,0);
  lcd.print("                    ");
  lcd.setCursor(0,0);
  lcd.print("Arus  : ");
  lcd.print(arus_char_1);
  lcd.setCursor(17,0);
  lcd.print("mA");
  
  lcd.setCursor(0,1);
  lcd.print("                    ");
  lcd.setCursor(0,1);
  lcd.print("Volt1 : ");
  lcd.print(tegangan1_char);
  lcd.setCursor(17,1);
  lcd.print("V");
  
  lcd.setCursor(0,2);
  lcd.print("                    ");
  lcd.setCursor(0,2);
  lcd.print("Power : ");
  lcd.print(power1_char);
  lcd.setCursor(17,2);
  lcd.print("mW");


  lcd.setCursor(0,3);
  lcd.print("                    ");
  lcd.setCursor(0,3);
  lcd.print("Energi: ");
  lcd.print(energi);
  lcd.setCursor(17,3);
  lcd.print("kWh");


  // kirim ke socket
  //String data = voltchar + "," + arus_char_1 + "," + power_char
  String senddata = (String)tegangan1_char + ',' +(String) arus_char_1 + ','+ (String)power1_char;
  if(SocketClient.connected())
  {
    SocketClient.print(senddata);

    int msg_fromServer = SocketClient.read();
    Serial.println(msg_fromServer);

    if(msg_fromServer == 1)
    {
      selected_channel = 1;
      change_channel = true;
    }
    else if (msg_fromServer == 2)
    {
      selected_channel = 2;
      change_channel = true;
    }
    else{
      change_channel = false;
      // do nothing
      ;
    }
  }

  delay(sample_interval) ;
  count++; // 100 ms increment
}