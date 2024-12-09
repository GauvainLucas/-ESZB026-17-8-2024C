const int analogInPin = A0;            // o potenciômetro esta ligado ao pino A0
int iniciaColeta = 0;
int iniciaIntervalo = 0;
char charRecebido;                     // cria uma variavel para armazenar o caractere recebido
long anterior, agora, intervalo, ultimaMedicao;
int meu_delay = 100;

void setup(){
   // Configura a serial: baud rate de 115200, 8-bit, sem paridade, 1 stop bit
   Serial.begin(115200, SERIAL_8N1);
   anterior = millis();
}

void loop(){
   if (Serial.available()){            // verifica se recebeu algum comando
      charRecebido = Serial.read();    // le o caractere recebido
      switch ( charRecebido ){
          case 'i':                    // inicia coleta
             iniciaColeta = 1;
             break;
             
          case 'p':                    // para a coleta
             iniciaColeta = 0;
             break;

          case 'c':
             Serial.write(intervalo & 0xFF);
             Serial.write(intervalo >> 8 & 0xFF);

             break;
             
          case 'd':
            // aaa = aaa + 1;
            meu_delay+=5;
            break;
             
          case 'e':
            // aaa = aaa - 1;            
            meu_delay-=5;
            break;
                
             
          default:                     // outro comando, ignora...
             break;
      }
   }
   if ( iniciaColeta == 1 ){
       int valor = analogRead(analogInPin); // le valor no pino A0 usando conversor ADC de 10-bit
       Serial.write(valor & 0xFF);          // envia byte menos significativo
       Serial.write(valor >> 8);            // envia byte mais significativ
       agora = millis();
       intervalo = agora-anterior;
       anterior = agora;
   }
   delay(meu_delay);                          // aguarda 100ms
   

}
