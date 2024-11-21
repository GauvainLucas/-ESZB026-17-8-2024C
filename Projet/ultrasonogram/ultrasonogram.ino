// Original idea by Milan Karakaš, https://wildlab.org (C)2016
// Made wild idea to use analog echo reading - NOT echo pin
// from HC-SR04 ultrasonic module, just solder one wire at
// collector of the transistor as is shown on my website:
// https://wildlab.org/index.php/arduino-ulstrasonic-radar/
// This sketch "burn" onto your favorite Arduino (uno, nano....)
// and enjoy in experimenting with ultrasound "Sonograms". :o)
// Pay attention to Serial.begin(115200) because there are lot
// of data sending in short period, so both: Arduino board and
// Processing program on your computer can communicate without
// los of data. Processing you can find here: https://processing.org/
// Bonus notice: Anyone who first make this Radar, please contact
// me in the comment section below this page:
// https://wildlab.org/index.php/arduino-ulstrasonic-radar/
// And your work will be published as "Showcase" for other people 
// as an example. Later I will figure out how to reward you. Thanks. 

#include <Servo.h>

#define SERVO_PWM_PIN 6
#define ANGLE_BOUNDS 80
#define ANGLE_STEP 1

int angle = 0;
int dir = 1;
int i,j;
float strength[80]; //40 analog readings send to your computer for "Processing" program
Servo myservo;
int analog_pin = A0; //analog pin A0 on arduino nano, uno, mega....

void setup() 
{
pinMode(2,OUTPUT);
Serial.begin(115200);
//Serial.begin(250000);
myservo.attach(SERVO_PWM_PIN);//later will be attached/detached, but once should start for first time
}

void loop() 
{
  getValues();
  Serial.print(-angle, DEC);      //first parameter send to your computer for Processing program
  // Pay Attention! There is "-angle" because some servoes may do it in wrong direction. If servo and image
  // on your computer does not match, put there "angle" instead "-angle". This will reverse servo direction                        
  for (i=0;i<80;i++)              //will be good to use variable instead fixed value for number of reading points
   {                              //for later experimenting with number of analog read echo points
     Serial.print(",");           // all data separated by coma (',')
     Serial.print(strength[i],0); // Atention! This is not for debugging - Processing program will use it
                                  // for visualisation (reading from COMxx port)
   }
  Serial.println(); //not printing anything, just new row, and back to the first place
  myservo.write(angle + ANGLE_BOUNDS); //servo should move one step
  if (angle >= ANGLE_BOUNDS-40 || angle <= -ANGLE_BOUNDS+40)
   {
     dir = -dir;
   }
  angle += (dir*ANGLE_STEP);
  delay(50); // alow some time for +5V to settle down, because servo can draw some current and make analog read error
             // DO NOT go below 10 mS - this value is experimentally get by oscilloscope, else strange "rays" may occur on radar
 }

int getValues() //function which read analog echo and return array of analog values
{
  myservo.detach(); //very important! this command disable PWM - which make interference during analog read
  delay(2); //wait additionally 2 mS for RF noise to settle down (first few centimeters)
  digitalWrite(2,1); //this triggers sensor
  delayMicroseconds(1); //although it is set to 1 uS, it gives actually 4 uS, which is sufficient to trigger HC-SR04 ultrasound ...
  digitalWrite(2,0);//this is end of triggering sensor
 // delay(1);//lets avoid crosstalk between emitter and receiver in first millisecond or two
 // NO! let it be: if this delay is added, then whole screen is wrong - missing some components and distorted...
 // As a result of avoiding this delay, "origin" of the radar pulses will be with some false reading, but not a problem
  for (j=0;j<80;j++) //lets make array of j elements
   {
 // int str= ((analogRead(analog_pin)*5.00)/1024)*pow(i,2);   // too long to execute, also not using constrain below
        strength[j]=(analogRead(analog_pin)*0.0025)*pow(i,2); // "dynamic amplification" by exponent^2 of i *5
                                                              // Since amplitude of ultrasound fall with square of the distance,
                                                              // "pow(i,2)" is actually i^2 (i squared). You may experiment with
                                                              // additional amplification by factor of 5 in example above
                                                              // too much, and noise will be visible, too low, and reflectin will be
                                                              // weak, yet maybe better "gray scale" than too high values
   //strength[j]=constrain(str,0,255); //since "Processing" program will use max values between 0 and 255, lets make some limits
                                       //but disabled because it "stills" some valuable mathematic time of the MCU
  }
  myservo.attach(SERVO_PWM_PIN); //now let servo PWM signal to continue for next step before back into main loop
  return strength[80]; // returning array of analog read echo values, you may experiment with this number of points. 
}                      // Just remember to change sketch on Processing so that number of this readings are correct
                       // Data send to your computer is angle + this number of samples. In Processing use array of 41 numbers
                       // First number will be from -80 to 80, which indicates angle, and the rest of numbers ranging fom 0 to 255
                       // representing amplitude of the echoed ultrasound.  
