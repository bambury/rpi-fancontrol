#!/usr/bin/env python
#
# Based on:
# https://github.com/jane-t/rpi-fanshim
# http://www.philrandal.co.uk/blog/archives/2019/07/entry_214.html
# https://forum-raspberrypi.de/forum/thread/43568-fan-shim-steuern/
# and:
# https://github.com/pimoroni/fanshim-python/blob/master/examples/automatic.py
# fanshim.py By Maxime Vincent (maxime [dot] vince [at] gmail [dot] com)
#
import atexit
import colorsys
import argparse
import time
import sys
import subprocess
import os

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs

sys.path.append('/storage/.kodi/addons/virtual.rpi-tools/lib')
import RPi.GPIO as GPIO

msgdialogprogress = xbmcgui.DialogProgress()

addon_id = 'service.fancontrol'
selfAddon = xbmcaddon.Addon(addon_id)
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
addonfolder = xbmc.translatePath(selfAddon.getAddonInfo('path'))

FAN = 14

fan_enabled = False

debug_mode = selfAddon.getSetting('debug_mode') == 'true'
on_threshold = int(selfAddon.getSetting('fan_on_temp'))
off_threshold  =  int(selfAddon.getSetting('fan_off_temp'))
delay =  int(selfAddon.getSetting('delay'))

noled = True

xbmc.log("Fan On :" + str(on_threshold) + " Off " + str(off_threshold),level=xbmc.LOGINFO)
xbmc.log("Delay :" + str(delay) + " Hide Led: " + str(noled) + " Debug : " + str(debug_mode),level=xbmc.LOGINFO)

def init():
    # For FAN
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN, GPIO.OUT)
    GPIO.output(FAN, False)
    return()

def _exit():
    GPIO.cleanup()

def set_fan(status):
    global fan_enabled
    changed = False
    if status != fan_enabled:
        changed = True
    GPIO.output(FAN, status)
    fan_enabled = status
    return changed

def watch_temp():
    global fan_enabled
    cpu_temp = get_cpu_temp()
    if debug_mode:
        f = get_cpu_freq()
        xbmc.log("Fan Status: " + str(fan_enabled) + " temp:" + str(cpu_temp) + " Freq " + str(f) + " %=",level=xbmc.LOGINFO)

    if fan_enabled == False and cpu_temp >= on_threshold:
         xbmc.log(str(cpu_temp) + "Enabling fan!" + " temp:" + str(cpu_temp),level=xbmc.LOGINFO)
         set_fan(True)
    if fan_enabled == True and cpu_temp <= off_threshold:
         xbmc.log(str(cpu_temp) + " Disabling fan!" + " temp:" + str(cpu_temp),level=xbmc.LOGINFO)
         set_fan(False)
    return();

def get_cpu_temp():
    return float(subprocess.check_output(['vcgencmd', 'measure_temp'])[5:-3])

def get_cpu_freq():
    return float(subprocess.check_output(['vcgencmd', 'measure_clock', 'arm'])[14:-1])/1000000

init()
xbmc.log("Starting Fan Control",level=xbmc.LOGINFO)
if __name__ == '__main__':
    monitor = xbmc.Monitor()

while not monitor.abortRequested():
    # Sleep/wait for abort for x seconds
    if monitor.waitForAbort(delay):
            # Abort was requested while waiting. We should exit
            xbmc.log("Ending Fan Control",level=xbmc.LOGINFO)
            break


    watch_temp()

xbmc.log("Fan Control Closed",level=xbmc.LOGINFO)
