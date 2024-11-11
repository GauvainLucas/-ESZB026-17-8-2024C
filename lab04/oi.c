#include<stdio.h>
#include<fcntl.h>
#include<unistd.h>
#include<termios.h>
#include<string.h>
#include<stdio.h>
#include<stdlib.h>
#include <wiringPi.h>
#include <softPwm.h>

int main(){
   int file, count, valor;

   if ((file = open("/dev/ttyACM0", O_RDWR | O_NOCTTY | O_NDELAY))<0){
      perror("Falha ao abrir o arquivo.\n");
      return -1;
   }
   struct termios options;
   tcgetattr(file, &options);
   options.c_cflag = B115200 | CS8 | CREAD | CLOCAL;
   options.c_iflag = IGNPAR | ICRNL;
   tcflush(file, TCIFLUSH);
   tcsetattr(file, TCSANOW, &options);
   usleep(100000);
   
   int pino_PWM = 23;                         // pwm por software na GPIO23
   int range = 100;                           // periodo do PWM = 100us*range
   int brilho;
   wiringPiSetupGpio();                       // usar a numeracao GPIO, nao WPi
   pinMode(pino_PWM,OUTPUT);	           // configura GPIO23 como saida
   softPwmCreate(pino_PWM, 1, range);         // inicializa PWM por software

   
   while (1) {
      unsigned char receive[100];
      if ((count = read(file, (void*)receive, 100))<0){
	 perror("Falha ao ler da entrada.\n");
	 return -1;
      }
      if (count==0) printf("Nao havia dados para led.\n");
      else {
	 receive[count]=0;  // o Arduino nao envia o caractere nulo (\0=0)
	 printf("Foram lidos [%d] caracteres: %s\n",count,receive);
	 
	 valor = atoi(receive);
	 
	 printf("li vlaor %d\n",valor);
      }
      
      brilho = valor*100.0/1023;
      softPwmWrite (pino_PWM, valor);
      usleep(100000);
   }
   close(file);
   return 0;
}
