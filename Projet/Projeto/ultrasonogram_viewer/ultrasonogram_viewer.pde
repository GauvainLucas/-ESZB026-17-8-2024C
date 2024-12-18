// Original idea by Milan Karakaš, 2016, https://wildlab.org
// https://wildlab.org/index.php/arduino-ulstrasonic-radar/
// Revision 1.01 - sorry, but not yet cleaned for not used parts
// some old stuff remained, because had hard time to figure out
// how to work in Processing. Thanks for understanding.
// New big screen size; 1920 x 1024 for those who have HD screen
// Or, down below should be math slightly changed

import processing.serial.*;

int SIDE_LENGTH = 1000;
int ANGLE_BOUNDS = 80;
int ANGLE_STEP = 2;
int HISTORY_SIZE = 10;
int POINTS_HISTORY_SIZE = 500;
int MAX_DISTANCE = 100;

int angle;
int distance;
int[] echoes = new int[80]; // Now with more points; 80 instead old 40 

int radius;
float x, y;
float leftAngleRad, rightAngleRad;

float[] historyX, historyY;
Point[] points; //ovo je primjer više točaka, no samo jedna je "prošla" kroz funkciju (angle, ->distance)

int centerX, centerY;

String comPortString;
Serial myPort;

void setup() {
  size(1024, 600);// was 1024,600 - for 80 points it is better to have bigger screen
  noStroke();
  //smooth();
  rectMode(CENTER);
background(0);
  radius = SIDE_LENGTH / 2;
  centerX = width / 2;
  centerY = height;
  angle = -40;
  leftAngleRad = radians(-ANGLE_BOUNDS) - HALF_PI;
  rightAngleRad = radians(ANGLE_BOUNDS) - HALF_PI;

  historyX = new float[HISTORY_SIZE];
  historyY = new float[HISTORY_SIZE];
  points = new Point[POINTS_HISTORY_SIZE];

  myPort = new Serial(this, "/dev/ttyACM0", 115200);
 //  myPort = new Serial(this, Serial.list()[1], 250000); //just tested in debugging process, ignore
  myPort.bufferUntil('\n'); // Trigger a SerialEvent on new line
}


void draw() //ovo je totalno okay, ne diraj
{
  drawFoundObjects(angle, echoes); //was: drawFoundObjects(angle, distance);
}

void drawFoundObjects(int angle, int echoes[]) //was: void drawFoundObjects(int angle, int distance) 
{
  int n;
for ( n=1;n<80;n++)
{
//float distance = n*6.25; //for "small screen, or one with only 40 points
float distance = n*12.5;// "zoom" options   -  much bigger screen
  if (distance > 0) 
  {
    float radian = radians(angle);
    x = distance * sin(radian);
    y = distance * cos(radian);
    int px = (int)(centerX + x);
    int py = (int)(centerY - y);
    points[0] = new Point(px, py); //was: points[0] = new Point(px, py);
  } else 
  {
    points[0] = new Point(0, 0);
  }
    for (int i=0; i<POINTS_HISTORY_SIZE; i++) //not resolved yet whether it needs to be here or not...
  {
    Point point = points[i];//was: Point point = points[i];
    if (point != null) 
    {
      int x = point.x;
      int y = point.y;  
      if (x==0 && y==0) continue;
  
      // NEW, "green" look of the screen :D
      //fill(20,echoes[n],40); //or "fill(255,echoes[n]", or "fill(echoes[n],echoes[n])" - gives various graphic result
      fill(echoes[n]);
      //first number in "fill(number,alpha) is brightnes of elypse, and second is "alpha" whatsoever, different effect
      noStroke();
      ellipse(x, y, 5, 5); //variation on 15,15 if necessary: ellipse(x, y, size, size); //various spot sizes...
    }
  }

 }
}

void drawRadar() 
{
  stroke(100);
  noFill();

  // part of the circle distance from the center
  for (int i = 0; i <= (SIDE_LENGTH / 100); i++) {
    arc(centerX, centerY, 100 * i, 100 * i, leftAngleRad, rightAngleRad);
  }

  // angle indicators
  for (int i = 0; i <= (ANGLE_BOUNDS*2/20); i++) {
    float angle = -ANGLE_BOUNDS + i * 20;
    float radAngle = radians(angle);
    line(centerX, centerY, centerX + radius*sin(radAngle), centerY - radius*cos(radAngle));
  }
}

void serialEvent(Serial cPort) 
{

  comPortString = cPort.readString();
  if (comPortString != null) 
  {

    comPortString=trim(comPortString);
    String[] values = split(comPortString, ',');
    try 
    {
      angle = Integer.parseInt(values[0]); //just first element of array is angle, everything else are echoes analog values
      if (angle == 40) {
      println("END");
      }
      for (int n=1; n<80; n++) //new 80 elements instead 40
      {
        echoes[n]= Integer.parseInt(values[n]);
      }
    } 
    catch (Exception e) {}
  }

}

class Point {
  int x, y;

  Point(int xPos, int yPos) {
    x = xPos;
    y = yPos;
  }

  int getX() {
    return x;
  }

  int getY() {
    return y;
  }
}
