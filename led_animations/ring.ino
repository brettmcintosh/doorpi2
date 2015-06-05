// This file contains all the LED animations for the LED ring.  It also configures the 
// teensy to accept commands over UART to start/stop the animations.

#include "FastLED.h"

#define NUM_LEDS 24
#define DATA_PIN 14

#define RESTART_ADDR       0xE000ED0C
#define READ_RESTART()     (*(volatile uint32_t *)RESTART_ADDR)
#define WRITE_RESTART(val) ((*(volatile uint32_t *)RESTART_ADDR) = (val))


// create leds array
CRGB leds[NUM_LEDS];

long s;
int counter;


void setup(){
	FastLED.addLeds<WS2811, DATA_PIN, GRB>(leds, NUM_LEDS);

	Serial.begin(9600);

};


void loop(){
//======== serial receive mode ============

	if(Serial.available()){
		s = Serial.read();
	}

	if(s == 'r'){
		// Serial.println("Rainbowing...");
		s = 'x';
		rainbow(50);
		fill_black();
	}

	if(s == 'm'){
		// Serial.println("Alarming...");
		s = 'x';
		alarm(85);
		fill_black();
	}

	if(s == 'c'){
		// Serial.println("Stacking...");
		s = 'x';
		ringstack(50, CRGB::Red);
		fill_black();
	}

	if(s == 'u'){
		// Serial.println("Unstacking...");
		s = 'x';
		ringunstack(50, CRGB::Red);
		fill_black();
	}

        if(s == 'w'){
		// Serial.println("Unstacking white...");
		s = 'x';
		ringunstackwhite(50, CRGB::Red);
		fill_black();
	}

        if(s == 'W'){
                // Serial.println("White...");
                s = 'x';
                fill(CRGB::White, 200, 3000);
                fill_black();
        }

	delay(5);


//======== Pattern Tests ==============

	// fill_black(1);

	// chase(50, CRGB::Red);
	// chase(50, CRGB::Green);
	// chase(50, CRGB::Blue);

	// fill(CRGB::Red, 100);
	// fill(CRGB::Green, 100);
	// fill(CRGB::Blue, 100);

	// fill(CRGB::White, 100);

	// countdown_to_alarm(333, CRGB::Red);

	// rainbow(50);
	// fill_black();
	// delay(1000);

	// police(25);

	// ringstack(50, CRGB::Red);
	// ringunstack(50, CRGB::Red);

	// alarm(85);

}



void fill_black(){
	fill_solid( &(leds[0]), NUM_LEDS, CRGB::Black);
	FastLED.show();
}

void chase(int wait, CRGB color){
	for(int i = 0; i<NUM_LEDS; i++){
		leds[i] = color;
		leds[i] %= 20;

		if(i != 0){
			leds[i-1] = CRGB::Black;
		}else{
			leds[23] = CRGB::Black;
		}

		FastLED.show();
		delay(wait);
	}
}

void fill(CRGB color, int brightness, int wait){
	for(int i=0; i<NUM_LEDS; i++){
		leds[i] = color;
		leds[i] %= brightness;
	}

	FastLED.show();
        delay(wait);
}

void countdown_to_alarm(int wait, CRGB color){
	for(int i=0; i<NUM_LEDS; i++){
		leds[i] = color;
		leds[i] %= 75;
	}
	FastLED.show();
	delay(wait);

	for(int i=0; i<NUM_LEDS; i++){
		leds[i] = CRGB::Black;
		FastLED.show();
		delay(wait);
	}
	delay(1000);
}

void countdown_to_arm(int wait, CRGB color){
	for(int i=0; i<NUM_LEDS; i++){
		leds[i] = color;
		leds[i] %= 20;
	}
	FastLED.show();
	delay(wait);

	for(int i=0; i<NUM_LEDS; i++){
		leds[i] = CRGB::Black;
		FastLED.show();
		delay(wait);
	}
	delay(1000);
}

void rainbow(int wait){
	for(int i=0; i<75; i++){
		for(int j=0; j<NUM_LEDS; j++){
			leds[j] = CHSV((j+i)*10, 255, 100);
		}
		FastLED.show();

		if(Serial.available()){
			s = Serial.read();
		}
		if(s == 'T'){
			goto escape;
		}
		delay(wait);
	}
	escape:
	;
}

void police(int wait){
	for(int t=0; t<10; t++){
		for(int offset=0; offset<NUM_LEDS; offset++){
			for(int h1=0; h1<(NUM_LEDS/2)+1; h1++){
				leds[(h1+offset)%NUM_LEDS] = CRGB::Red;
				leds[(h1+offset)%NUM_LEDS] %= 80;
			}
			for(int h2=(NUM_LEDS/2); h2<NUM_LEDS; h2++){
				leds[(h2+offset)%NUM_LEDS] = CRGB::Blue;
				leds[(h2+offset)%NUM_LEDS] %= 80;
			}
			FastLED.show();
			delay(wait);
		}
	}
}

void ringstack(int wait, CRGB color){
	fill_black();
	int length = NUM_LEDS;
	for(int i=0; i<NUM_LEDS; i++){
		for(int j=0; j<length; j++){
			leds[j] = color;
			leds[j] %= 50;
			if(j != 0 || j != (length - 1)){
				leds[j-1] = CRGB::Black;
			}
		FastLED.show();

		if(Serial.available()){
			s = Serial.read();
		}
		if(s == 'T'){
			goto escape;
		}
		delay(wait);
		}
	length--;
	}
	fill(color, 50, 0);
	// delay(5000);
	escape:
	;
}

void ringunstack(int wait, CRGB color){
	fill(color, 50, 0);
	int length = 0;
	for(int i=0; i<NUM_LEDS; i++){
		for(int j=NUM_LEDS-length; j<=NUM_LEDS; j++){
			leds[j] = color;
			leds[j] %= 50;
			if(j!=0){
				leds[j-1] = CRGB::Black;
			}
		FastLED.show();
		
		if(Serial.available()){
			s = Serial.read();
		}
		if(s == 'T'){
			goto escape;
		}
		delay(wait);
		}
	length++;
	}
	fill_black();
	// delay(5000);
	escape:
	;
}

void ringunstackwhite(int wait, CRGB color){
	fill(CRGB::White, 200, 3000);
	int length = 0;
	for(int i=0; i<NUM_LEDS; i++){
		for(int j=NUM_LEDS-length; j<=NUM_LEDS; j++){
			leds[j] = color;
			leds[j] %= 50;
			if(j!=0){
				leds[j-1] = CRGB::Black;
//                                leds[j-1] %= 200;
			}
		FastLED.show();
		
		if(Serial.available()){
			s = Serial.read();
		}
		if(s == 'T'){
			goto escape;
		}
		delay(wait);
		}
	length++;
	}
	fill_black();
	// delay(5000);
	escape:
	;
}

void alarm(int wait){
	for(int t=0; t<10; t++){
		for(int i=0; i<4; i++){
			for(int j=0; j<NUM_LEDS; j++){
				leds[j] = CRGB::Red;
				// leds[j] %= 50;
				if(j==(0+i)%24 ||
				   j==(4+i)%24 ||
				   j==(8+i)%24 ||
				   j==(12+i)%24 ||
				   j==(16+i)%24 ||
				   j==(20+i)%24 ){
					leds[j] = CRGB::Black;
					// leds[j] %= 50;
				}
			}
			FastLED.show();
			if(Serial.available()){
				s = Serial.read();
			}
			if(s == 'T'){
				goto escape;
			}
			delay(wait);
		}
	}
	escape:
	;
}
