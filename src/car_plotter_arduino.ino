/*
 * car_plotter_arduino - reads distance measurements from VL53L0X TimeOfLight sensor,
 * and sample linear potentiometer - writes the results to the USB serial and TM1636 display.
 * 
 * Pinout:
 *  ┌─────────┬─────────┬────────┬─────┐
 *  │ Arduino │ VL53L0X │ TM1636 │ POT │
 *  ├─────────┼─────────┼────────┼─────┤
 *  │ VCC     │ VCC     │ VCC    │ VCC │
 *  │ GND     │ GND     │ GND    │ GND │
 *  │ A4      │ SDA     │        │     │
 *  │ A5      │ SCL     │        │     │
 *  │ 4       │         │ DIO    │     │
 *  │ 5       │         │ CLOCK  │     │
 *  │ 6       │         │ STROBE │     │
 *  │ A0      │         │        │ OUT │
 *  └─────────┴─────────┴────────┴─────┘
 */
#include <Arduino.h>

#define UART_BAUDRATE				(115200)
#define PRINT_MS					(10)
#define USE_TM1636					// undefine if not connected
#define USE_ADAFRUIT_LIB			// undefine to use pololu lib
#define TEST_POT_PIN				(A0) // undefine if not connected

#ifdef USE_TM1636
	#include <TM1638plus.h>			// https://github.com/gavinlyonsrepo/TM1638plus
	#define TM1636_DIO_PIN			(4)
	#define TM1636_CLOCK_PIN		(5)
	#define TM1636_STROBE_PIN		(6)
	TM1638plus tm(TM1636_STROBE_PIN, TM1636_CLOCK_PIN, TM1636_DIO_PIN);
#endif
#ifdef USE_ADAFRUIT_LIB
	#include <Adafruit_VL53L0X.h>	// https://github.com/adafruit/Adafruit_VL53L0X
	Adafruit_VL53L0X tof;
	VL53L0X_RangingMeasurementData_t measurement;
#else
	#include <Wire.h>
	#include <VL53L0X.h>			// https://github.com/pololu/vl53l0x-arduino
	VL53L0X tof;
#endif

uint16_t last_dist;
uint32_t last_print_ms;

void setup()
{
	Serial.begin(UART_BAUDRATE);	// setup UART ("Serial")

#ifdef USE_TM1636					// setup display if needed
	tm.displayBegin();
	tm.reset();
#endif

#ifdef USE_ADAFRUIT_LIB				// setup TOF sensor
	while (!tof.begin()) {
#else
	Wire.begin();
	tof.setTimeout(500);
	while (!tof.init()) {
#endif
		Serial.println(F("Failed to detect VL53L0X"));
		delay(1000);
	}
#ifndef USE_ADAFRUIT_LIB
	tof.startContinuous();
#endif
}

void loop()
{
	char buff[32];
	char *text = "dst";
	uint16_t dist = 0;
	uint32_t cur_ms = millis();

#ifdef USE_ADAFRUIT_LIB				// read distance from TOF sensor
	tof.rangingTest(&measurement, false);
	if (measurement.RangeStatus != 4)
		dist = measurement.RangeMilliMeter;
#else
	dist = sensor.readRangeContinuousMillimeters();
	if (sensor.timeoutOccurred())
		dist = 0;
#endif

	if (dist) {
#ifdef TEST_POT_PIN					// overwrite distance with potentiometer if sensor is covered
		if (dist < 30) {
			dist = 1023 - analogRead(TEST_POT_PIN);
			text = "pot";
		}
#endif
		last_dist = dist;
	}

	if (cur_ms - last_print_ms > PRINT_MS) {
		last_print_ms = cur_ms;
#ifdef USE_TM1636					// write to display and LEDs if needed
		sprintf(buff, "%s %04d", text, last_dist);
		tm.displayText(buff);
		tm.setLEDs(0x0100 << (last_dist / 125));
#endif
		sprintf(buff, "%04d\n", last_dist);
		Serial.print(buff);			// write to uart
	}

	delay(1);
}
