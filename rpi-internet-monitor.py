#!/usr/bin/env python
import subprocess
import sys
import time
import RPi.GPIO as GPIO

GPIO_GREEN_LIGHT = 32      # led for internet working
GPIO_AMBER_LIGHT = 36      # led for internet marginally working
GPIO_RED_LIGHT = 38        # led for internet is not working
GPIO_BLUE_LIGHT = 40       # indication script is collecting information (running)
DELAY_BETWEEN_PINGS = 2    # delay in seconds
DELAY_BETWEEN_TESTS = 360  # delay in seconds between consecutive tests (time to wait to perform next test)
PING_LOOP = 2              # times we are looping over the site list
NUMBER_OF_TEST_CYCLES = 4  # number of test cycles of the LED we are processing
SUCCESS_FACTOR = .75       # [e.g. .75] = 75%; cut-off % between green / yellow: higher then this: green, lower: yellow
                           # Set this % wisely: depending on the amount of 'test sites'
TEST = 0

SITES = ["google.com", "usaa.com", "amazon.com", "fast.com"]
#SITES = ["ddffggsseerrbb.net"]
#SITES = ["localhost", "127.0.0.1", "8.8.8.8"]

# print messages for debugging when indicator is set
def debug_message(debug_indicator, output_message):
  if debug_indicator:
    print output_message

# issue Linux ping command to determine internet connection status
def ping(site):
  cmd = "/bin/ping -c 1 " + site
  try:
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
  except subprocess.CalledProcessError, e:
    debug_message(debug, site + ": not reachable")
    return 0
  else:
    debug_message(debug, site + ": reachable")
    return 1

# ping the sites in the site list the specified number of times and calculate the percentage of successful pings
def ping_sites(site_list, wait_time, times):
  successful_pings = 0
  attempted_pings = times * len(site_list)
  for t in range(0, times):
    for s in site_list:
      successful_pings += ping(s)
      time.sleep(wait_time)
  debug_message(debug, "Percentage successful: " + str(int(100 * (successful_pings / float(attempted_pings)))) + "%")
  return successful_pings / float(attempted_pings)   # return percentage successful 

def led_amber_on():                          # turn the amber led on
  debug_message(debug, ">>> Turn Red OFF; Turn Amber ON; Turn Green OFF")
  GPIO.output(GPIO_RED_LIGHT, False)
  GPIO.output(GPIO_AMBER_LIGHT, True)
  GPIO.output(GPIO_GREEN_LIGHT, False)

def led_green_on():                          # turn the green led on
  debug_message(debug, ">>> Turn Red OFF; Turn Amber OFF; Turn Green ON")
  GPIO.output(GPIO_RED_LIGHT, False)
  GPIO.output(GPIO_AMBER_LIGHT, False)
  GPIO.output(GPIO_GREEN_LIGHT, True)

def led_red_on():                            # turn the red led on
  debug_message(debug, ">>> Turn Red ON; Turn Amber OFF; Turn Green OFF")
  GPIO.output(GPIO_RED_LIGHT, True)
  GPIO.output(GPIO_AMBER_LIGHT, False)
  GPIO.output(GPIO_GREEN_LIGHT, False)

def led_blue_on():
  debug_message(debug, ">>> Turn Blue ON")
  GPIO.output(GPIO_BLUE_LIGHT, True)

def led_blue_off():
  debug_message(debug, ">>> Turn Blue OFF")
  GPIO.output(GPIO_BLUE_LIGHT, False)

def led_all_off():                           # turn all of the leds off
  debug_message(debug, ">>> Turn Red OFF; Turn Amber OFF; Turn Green OFF; Turn Blue OFF")
  GPIO.output(GPIO_RED_LIGHT, False)
  GPIO.output(GPIO_AMBER_LIGHT, False)
  GPIO.output(GPIO_GREEN_LIGHT, False)
  GPIO.output(GPIO_BLUE_LIGHT, False)

def led_test():                              # flash all of the leds in sequence five times
  debug_message(debug, "Testing Lights")
  TEST_DELAY = 0.4                            # 0.1 == tenth of a second delay   
  TEST_DELAY_CYCLE = 2  
  for i in range(0, NUMBER_OF_TEST_CYCLES):
    time.sleep(TEST_DELAY)
    led_blue_on()
    led_red_on()
    time.sleep(TEST_DELAY)
    led_amber_on()
    time.sleep(TEST_DELAY)
    led_green_on()
    time.sleep(TEST_DELAY)
    led_blue_off()
    time.sleep(TEST_DELAY_CYCLE)
  led_all_off()
  debug_message(debug, "Light test completed")
      
def setup():
  GPIO.setmode(GPIO.BOARD)      # setup the GPIO pins
  GPIO.setup(GPIO_GREEN_LIGHT, GPIO.OUT)
  GPIO.setup(GPIO_AMBER_LIGHT, GPIO.OUT)
  GPIO.setup(GPIO_RED_LIGHT, GPIO.OUT)
  GPIO.setup(GPIO_BLUE_LIGHT, GPIO.OUT)

  led_all_off()      # all leds off
  led_test()         # flash the leds to indicate the program is starting
  time.sleep(0.5)     # sleepytime
  led_amber_on()     # turn amber led on during the first test

if __name__ == '__main__': #Program starting from here 
  try:
    debug = False
    if len(sys.argv) > 1:
      if sys.argv[1] == "-debug":           # check to see if the user wants to print debugging messages
        debug = True
      else:
        print "unknown option specified: " + sys.argv[1]
        sys.exit(1)
    setup()                                 # Setting up the pins / running LED test
    while True:                             # main loop: ping sites, turn appropriate led on, wait, repeat
      if TEST > 9999999:
          TEST = 0
      TEST+=1
      debug_message(debug, "----- Test " + str(TEST) + " -----")
      led_blue_on()                         # Showing that we are collecting data ....
      success = ping_sites(SITES, DELAY_BETWEEN_PINGS, PING_LOOP)
      led_blue_off()                        # Showing that we are done collecting data ....
      if success == 0:                      # No success what so ever
        led_red_on()
        #led_green_on()
      elif success <= SUCCESS_FACTOR:       # sucess % is lower or equal to success factor
        led_amber_on()
      else:                                 # all is well
        led_green_on()
        #led_amber_on()
        #led_red_on()
      debug_message(debug, "Waiting " + str(DELAY_BETWEEN_TESTS) + " seconds until next test.")
      time.sleep(DELAY_BETWEEN_TESTS)

  except KeyboardInterrupt:  
    print "\n Keyboard interuption"

  except ValueError:
    print "\n GPIO allocation is wrong", sys.exc_info()[0], sys.exc_info()[1]

  except:  
    print "\n Other exception", sys.exc_info()[0], sys.exc_info()[1]

  finally:
    GPIO.cleanup()

