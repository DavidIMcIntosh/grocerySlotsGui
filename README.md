Grocery Slots GUI
=================
This program will periodically check any of the Loblaws family of stores (Loblaws, Superstore, Valumart, Nofrills, Zehrs so far) for open grocery pick-up slots, displaying the open slots in a GUI widget.  By default, it will check every 5 minutes. The program can also announce via any Chromecast-compatible device (including Google Home) when a new spot opens.

Requirements
------------
* Python 3
* Python Libraries:
  * requests
  * python-dateutil
  * pychromecast
  * gtts


Installation and Startup
------------------------
1. Install Python3 if its not already on the system.
1. Install necessary Python libraries (there seems to be some variation about how to install the "dateutil" library):
    ```
    pip3 install --user requests python-dateutil pychromecast gtts
    ```
1. Find your Loblaws Store Location ID:
    1. Go to https://www.loblaws.ca/store-locator
    1. Choose a location and click the "Location Details" link
    1. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)
1. Run the script:
    ```
    python .\checkSlotsGui.py
    ```

Windows Self-Installer
----------------------
(This is not quite ready yet.)

The file checkSlotsGui.exe is a self-extracting zip file with a rudimentary install script.  For the average user, just download this file somewhere and double-click.

Technical details: The script should execute automatically after the self-extracting zip file unzips itself.  The install script will check for an installed version of Python.  If not found, it will attempt to install Python 3.8.2.  If install is successful, or if Python 3.8.2 or later is already installed, the script will then install the required Python libraries (see above).  Finally, the script will copy the checkSlotsGuy.py script to a checkSlotsGui directory in the users LocalAppDir and copy two start-up .cmd files to the users desktop.



GUI Usage reference
---------------
```
Usage: checkSlotsGui.py [--help] [--noChromeCast]
```

1. In the GUI, you will need to enter your Store Location string.
    1. Go to https://www.loblaws.ca/store-locator
    1. Choose a location and click the "Location Details" link
    1. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)
    
   The 4 digit string at the end of this URL must be entered into the Store Location box in the GUI.
   If you want your store location to always be the default when you start the GUI, adjust the "DEFAULT_STORE=1007" line in checkSlotsGui.py.
1. To poll your store periodically and show latest results, check the "Poll fo Openings" checkbox.  The frequency of checks is controlled with the "Check frequency (seconds):" entry.  The "Check Now" button (at any time) will cause an immediate check of the store.
1. Periodic polling needs to be restarted after any change to "Store Type".
1. If you want any change in the earliest timeslot to be announced on a Chromecast device (e.g. GoogleHome), click the "Start Server" button (this only needs to be done once), select the device with the "Broadcast Device" drop-down, and make sure the "Broadcast?" checkbox is checked.  These can be adjusted at any time, and the current values will be used at the next Check time.
1. Clicking the "Refresh Devices" at any time will refresh the list of available Chromecast devices.
1. Technical detail: the "Start Server" button starts up an HTTP server in a subdirectory "audio" of the directory containing the checkSlotsGui.py script.  If you want to start such a server manually in some other location, you do need to tell the GUI where the root of this server is with the "Chromecast Server Directory". The GUI will put the announcements into this directory for ChromeCast and then broadcast the announcement file to the chromecast devices.  Once you have a server running (either by pressing the "Start Server" button or starting a server in a separate console), you can test the Broadcast capabilities with the "Test" button, which will broadcast "Hello World" to the selected Broadcast device.
1. If you don't have any ChromeCast devices and want to prevent the GUI from even checking for ChromeCast devices, use the --noChromeCast startup option: 
    ```
    python .\checkSlotsGui.py --noChromeCast
    ```
1. If you DO have ChromeCast devices, and they are not appearing in the list of devices, it may be because an IP address is incorrect somewhere.  This can happen on systems with multiple network connections (e.g. wifi and hard-wired ethernet, or regular wifi plus a virtual VPN adapter).  In that case, if you know the IP address of your machine as seen on your WIFI or LAN network (by the other ChromeCase devices) you can type that into the ChromeCast Server IP (if you are running the server on your machine, e.g. if you use the "Start Server" button).  Or, you can adjust the LAN_OR_WIFI_SERVER_IP variable in the .py file to be the IP address of your WIFI router (where the other ChromeCast machines connect), and then the IP address in the GUI should be the correct IP address of your machine.
1. Technical detail: The Loblaws sites seem to keep their time-points in Universal Cordinated Time (UCT or GMT).  To display them in local time, they need to be adjusted via the TimeZoneOffset.  The default TimeZoneOffset is set up for Eastern Daylight Time.

History
-------
Based on ["groceryslots" (check_slots.py) by Jeffrey Wintersinger](https://github.com/jwintersinger/groceryslots). Other Loblaws family sites contributed by Daniel McIntosh.
