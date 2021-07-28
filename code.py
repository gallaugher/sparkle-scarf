# By John Gallaugher https://gallaugher.com  Twitter: @gallaugher
# YouTube: https://YouTube.com/profgallaugher
# Step-by-step video playlist demonstrating build at: https://bit.ly/bluefruit-school

# Run into build trouble? Adafruit runs a great help forum at:
# https://forums.adafruit.com - most questions are answered within an hour.
# Adafruit also has a discord channel at:
# http://adafru.it/discord

import board
import neopixel
import time

# imports needed for bluetooth
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

# import animations and colors
# While we don't use all of these animations and colors
# I import them all below in case you want to experiment with them.
# Full documentation for the adafruit_led_animation library is at:
# https://circuitpython.readthedocs.io/projects/led-animation/en/latest/api.html
import adafruit_led_animation
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowChase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.SparklePulse import SparklePulse
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.sequence import AnimateOnce
from adafruit_led_animation.color import (
    AMBER, #(255, 100, 0)
    AQUA, # (50, 255, 255)
    BLACK, #OFF (0, 0, 0)
    BLUE, # (0, 0, 255)
    CYAN, # (0, 255, 255)
    GOLD, # (255, 222, 30)
    GREEN, # (0, 255, 0)
    JADE, # (0, 255, 40)
    MAGENTA, #(255, 0, 20)
    OLD_LACE, # (253, 245, 230)
    ORANGE, # (255, 40, 0)
    PINK, # (242, 90, 255)
    PURPLE, # (180, 0, 255)
    RED, # (255, 0, 0)
    TEAL, # (0, 255, 120)
    WHITE, # (255, 255, 255)
    YELLOW, # (255, 150, 0)
    RAINBOW # a list of colors to cycle through
    # RAINBOW is RED, ORANGE, YELLOW, GREEN, BLUE, and PURPLE ((255, 0, 0), (255, 40, 0), (255, 150, 0), (0, 255, 0), (0, 0, 255), (180, 0, 255))
)

# setup bluetooth
ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)
# Give your CPB a unique name between the quotes below
advertisement.complete_name = "Scarf"

runAnimation = False
animation_number = -1
lightPosition = -1

# Update to match the pin connected to your NeoPixels
led_pin = board.A1
# UPDATE NUMBER BELOW to match the number of NeoPixels you have connected
num_leds = 20
# UPDATE color below if you want your light to show a different color at startup
defaultColor = AMBER
pickedColor = defaultColor

# I've programmed these values to set, then adjust the timing of animations
defaultTime = 0.1
minWaitTime = 0.01
hundredths = 0.01
tenths = 0.1
adjustedTime = defaultTime

# Sets up the Neopixel strand,initializing it to full brightness
strip = neopixel.NeoPixel(led_pin, num_leds, brightness=1.00, auto_write=False)
# demonstrate that you can pass in custom colors, too.
# the multi values in parens below are called a tuple value.
# this tuple has three values between 0 and 255.
customMaroonSolid = Solid(strip, color = (128, 0, 0))

# Comet animation has a dimming tail - sets the tail length
cometTailLength = int(num_leds/3) + 1

# Set LEDs to light up sold in the default color
strip.fill(pickedColor)
strip.write()

# The function runSelected will run the animation number stored in the value animation_number.
# This function is called in the while True: loop whenever an animation has been started, in while not ble.connected (when not connected to bluetooth)
# or while ble.connected (when connected to bluetooth). We call it in both locations so that if
# animations are started, then the user shuts off their phone or moves out of bluetooth range, the
# last selected animation will continue to run.
def runSelectedAnimation():
    if animation_number == 1:
        # larson()
        print("*** COMET or LARSON SCANNER ***")
        # I set bounc = False because that makes it look circular.
        # for a tie it's better to True so it looks like it bounces up and down.
        cometAnimation = Comet(strip, speed=adjustedTime, color=pickedColor, tail_length=cometTailLength, bounce=False)
        animations = AnimateOnce(cometAnimation)
        while animations.animate():
            pass
    elif animation_number == 2:
        print("*** PULSE ***")
        pulseAnimation = Pulse(strip, speed=adjustedTime, color=pickedColor, period=3)
        animations = AnimateOnce(pulseAnimation)
        while animations.animate():
            pass
    elif animation_number == 3:
        """ For some reason Sparkle runs indefinitely
        # so I skipped Sparkle & used SparklePulse
    """
        print("*** SPARKLE PULSE ***")
        sparklePulseAnimation = SparklePulse(strip, speed=adjustedTime, period=12, color=pickedColor)
        animations = AnimateOnce(sparklePulseAnimation)
        while animations.animate():
            pass
    elif animation_number == 4:
        print("*** RAINBOWS ***")
        # Rainbow: Entire strip starts RED and all lights fade together through rainbow
        rainbowAnimation = Rainbow(strip, speed=adjustedTime, period=2)
        # RainbowSparkle: Strip sparkes all one color (Red first), then sparkles all one color through rest of the rainbow
        rainbowSparkleAnimation = RainbowSparkle(strip, speed=adjustedTime, period=5, num_sparkles=int(num_leds/3))
        # RainbowComet - is a larson-style chase effect with comet in a rainbow pattern.
        rainbowCometAnimation = RainbowComet(strip, speed=adjustedTime, tail_length=cometTailLength, bounce=True)
        # the animation below runs all three animations, one after the other.
        animations = AnimateOnce(rainbowAnimation, rainbowCometAnimation, rainbowSparkleAnimation)
        while animations.animate():
            pass

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        if runAnimation == True:
            runSelectedAnimation()

    # Now we're connected so we don't need to advertise the device as one that you're able to connect to
    ble.stop_advertising()

    while ble.connected:
        if uart_server.in_waiting:
            try:
                packet = Packet.from_stream(uart_server)
            except ValueError:
                continue # or pass. This will start the next

            if isinstance(packet, ColorPacket):
                print("*** color sent")
                print("pickedColor = ", ColorPacket)
                runAnimation = False
                animation_number = 0
                strip.fill(packet.color)
                strip.write()
                pickedColor = packet.color
                # the // below will drop any remainder so the values remain Ints, which color needs
                fade_color = (pickedColor[0]//2, pickedColor[1]//2, pickedColor[2]//2)
                # reset light_position after picking a color
                light_position = -1

            if isinstance(packet, ButtonPacket):
                if packet.pressed:
                    if packet.button == ButtonPacket.BUTTON_1:
                        animation_number = 1
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_2:
                        animation_number = 2
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_3:
                        animation_number = 3
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_4:
                        animation_number = 4
                        runAnimation = True
                    elif packet.button == ButtonPacket.UP or packet.button == ButtonPacket.DOWN:
                        animation_number = 0
                        runAnimation = False
                        # The UP or DOWN button was pressed.
                        increase_or_decrease = 1
                        if packet.button == ButtonPacket.DOWN:
                            increase_or_decrease = -1
                        lightPosition += increase_or_decrease
                        if lightPosition >= len(strip):
                            lightPosition = len(strip)-1
                        if lightPosition <= -1:
                            lightPosition = 0
                        strip.fill([0, 0, 0])
                        strip[lightPosition] = pickedColor
                        strip.show()
                    elif packet.button == ButtonPacket.RIGHT:
                        # The RIGHT button was pressed.
                        runAnimation = True
                        # reset light_position after animation
                        lightPosition = -1
                        # new code below - you can delete code above
                        if adjustedTime <= 0.1:
                            adjustedTime = adjustedTime - hundredths
                        else:
                            adjustedTime = adjustedTime - tenths
                        if adjustedTime <= 0.0:
                            adjustedTime = minWaitTime
                    elif packet.button == ButtonPacket.LEFT:
                        # The LEFT button was pressed.
                        runAnimation = True
                        # reset light_position after animation
                        light_position = -1
                       # new code below - you can delete code above
                        if adjustedTime >= 0.1:
                            adjustedTime = adjustedTime + tenths
                        else:
                            adjustedTime = adjustedTime + hundredths
        if runAnimation == True:
            runSelectedAnimation()
    # If we got here, we lost the connection. Go up to the top and start
    # advertising again and waiting for a connection.
