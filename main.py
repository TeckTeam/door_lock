import RPi.GPIO as GPIO
import time
import os

password = "53604"
button_pin = 10
class Adafruit_CharLCD:

    # commands
    LCD_CLEARDISPLAY 		= 0x01
    LCD_RETURNHOME 		    = 0x02
    LCD_ENTRYMODESET 		= 0x04
    LCD_DISPLAYCONTROL 		= 0x08
    LCD_CURSORSHIFT 		= 0x10
    LCD_FUNCTIONSET 		= 0x20
    LCD_SETCGRAMADDR 		= 0x40
    LCD_SETDDRAMADDR 		= 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT 		= 0x00
    LCD_ENTRYLEFT 		= 0x02
    LCD_ENTRYSHIFTINCREMENT 	= 0x01
    LCD_ENTRYSHIFTDECREMENT 	= 0x00

    # flags for display on/off control
    LCD_DISPLAYON 		= 0x04
    LCD_DISPLAYOFF 		= 0x00
    LCD_CURSORON 		= 0x02
    LCD_CURSOROFF 		= 0x00
    LCD_BLINKON 		= 0x01
    LCD_BLINKOFF 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 		= 0x08
    LCD_CURSORMOVE 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 		= 0x08
    LCD_CURSORMOVE 		= 0x00
    LCD_MOVERIGHT 		= 0x04
    LCD_MOVELEFT 		= 0x00

    # flags for function set
    LCD_8BITMODE 		= 0x10
    LCD_4BITMODE 		= 0x00
    LCD_2LINE 			= 0x08
    LCD_1LINE 			= 0x00
    LCD_5x10DOTS 		= 0x04
    LCD_5x8DOTS 		= 0x00



    def __init__(self, pin_rs=12, pin_e=26, pins_db=[19, 11, 10, 9], GPIO = None):
	# Emulate the old behavior of using RPi.GPIO if we haven't been given
	# an explicit GPIO interface to use
        if not GPIO:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.pin_rs = pin_rs
            self.pin_e = pin_e
            self.pins_db = pins_db

            self.GPIO.setwarnings(False)
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setup(self.pin_e, GPIO.OUT)
            self.GPIO.setup(self.pin_rs, GPIO.OUT)

            for pin in self.pins_db:
                self.GPIO.setup(pin, GPIO.OUT)

        self.write4bits(0x33) # initialization
        self.write4bits(0x32) # initialization
        self.write4bits(0x28) # 2 line 5x7 matrix
        self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06) # shift cursor right

        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.displayfunction |= self.LCD_2LINE

        """ Initialize to default text direction (for romance languages) """
        self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

        self.clear()


    def begin(self, cols, lines):

        if (lines > 1):
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE
            self.currline = 0


    def home(self):

        self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
        self.delayMicroseconds(3000) # this command takes a long time!
	

    def clear(self):

        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        self.delayMicroseconds(3000)	# 3000 microsecond sleep, clearing the display takes a long time


    def setCursor(self, col, row):

        self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

        if ( row > self.numlines ): 
            row = self.numlines - 1 # we count rows starting w/0

        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))


    def noDisplay(self): 
	

        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def display(self):

        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):

	    self.displaycontrol &= ~self.LCD_CURSORON
	    self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
	

	    self.displaycontrol |= self.LCD_CURSORON
	    self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):


	    self.displaycontrol &= ~self.LCD_BLINKON
	    self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):

	    self.displaycontrol &= ~self.LCD_BLINKON
	    self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def DisplayLeft(self):
	

	    self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)


    def scrollDisplayRight(self):


	    self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);


    def leftToRight(self):

        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);


    def rightToLeft(self):
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):

        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self): 

        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def write4bits(self, bits, char_mode=False):

        self.delayMicroseconds(1000) # 1000 microsecond sleep

        bits = bin(bits)
        bits = bits[2:]
        bits = bits.zfill(8)

        self.GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)

        self.pulseEnable()

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i-4], True)

        self.pulseEnable()


    def delayMicroseconds(self, microseconds):
        seconds = microseconds / float(1000000)	# divide microseconds by 1 million for seconds
        sleep(seconds)


    def pulseEnable(self):
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
        self.GPIO.output(self.pin_e, True)
        self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
        self.GPIO.output(self.pin_e, False)
        self.delayMicroseconds(1)		# commands need > 37us to settle


    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.write4bits(ord(char),True)
class keypad():
    # CONSTANTS   
    KEYPAD = [
    [1,2,3,"A"],
    [4,5,6,"B"],
    [7,8,9,"C"],
    ["*",0,"#","D"]
    ]
     
    ROW = [11,12,13,15]
    COLUMN = [16,18,22,7]
     
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
     
    def getKey(self):
        while True:
            # Set all columns as output low
            for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.OUT)
                GPIO.output(self.COLUMN[j], GPIO.LOW)
            
            # Set all rows as input
            for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Scan rows for pushed key/button
            # A valid key press should set "rowVal"  between 0 and 3.
            rowVal = -1
            for i in range(len(self.ROW)):
                tmpRead = GPIO.input(self.ROW[i])
                if tmpRead == 0:
                    rowVal = i
                    
            # if rowVal is not 0 thru 3 then no button was pressed and we can exit
            """if rowVal < 0 or rowVal > 3:
                self.exit()
                return """
            
            # Convert columns to input
            for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # Switch the i-th row found from scan to output
            GPIO.setup(self.ROW[rowVal], GPIO.OUT)
            GPIO.output(self.ROW[rowVal], GPIO.HIGH)
    
            # Scan columns for still-pushed key/button
            # A valid key press should set "colVal"  between 0 and 2.
            colVal = -1
            for j in range(len(self.COLUMN)):
                tmpRead = GPIO.input(self.COLUMN[j])
                if tmpRead == 1:
                    colVal=j
                    
            # if colVal is not 0 thru 2 then no button was pressed and we can exit
            if colVal < 0 or colVal > 3:
                self.exit()
                return ""
    
            # Return the value of the key pressed
            self.exit()
            return self.KEYPAD[rowVal][colVal]
            
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
mode = False      
output = "Door-Lock\n Pin: "
if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad()
    lcd = Display()
    # Loop while waiting for a keypress
    digit = ""
    lcd.clear()
    while True:
        new = str(kp.getKey())
        if new:
            output = output + "*"
            lcd.clear()
            lcd.message(output)
            digit = digit + new    
            print(digit)
        if "*" in digit:
            digit = ""  
        if "#" in digit:
            digit = digit.replace("#", "")
            if digit == password or GPIO.input(button_pin) == GPIO.HIGH:
                if mode == False:
                    lcd.clear()
                    lcd.message("Door-Lock\n Locking the door")
                    os.system("sudo python3 door.py close")
                    print("Door close")
                    mode = True
                else:
                    lcd.clear()
                    lcd.message("Door-Lock\n Opening the door")
                    os.system("sudo python3 door.py open")
                    print("Door open")
                    mode = False
            else:
                lcd.clear()
                lcd.message("Wrong Password\n Please Try again:")
                print("Wrong Password. Please Try again.")
                time.sleep(5)
            print("Enter your Pin: ")
            lcd.clear()
            output = "Door-Lock\n Pin: "
            lcd.message(output)
            digit = ""
        time.sleep(0.35)