Grocery Slots GUI
=================
This program will periodically check any of the Loblaws family of stores (Loblaws, Superstore, Valumart, Nofrills, Zehrs so far) for open grocery pick-up slots, displaying the open slots in a GUI widget.  By default, it will check every 5 minutes. The program can also announce via any Chromecast-compatible device (including Google Home) when a new spot opens.

Requirements
------------
* Python 3

Usage
-----
1. Instally Python3 if its not already on the system.

2. Install necessary Python libraries (there seems to be some variation about how to install the "dateutil" library):

    ```
    pip3 install --user requests python-dateutil pychromecast gtts
    ```

3. Find your Loblaws Store Location ID:

    i. Go to https://www.loblaws.ca/store-locator
    
    ii. Choose a location and click the "Location Details" link
    
    iii. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)

4. Run the main script.

    ```
    python .\checkSlotsGui.py
    ```
    
GUI Usage reference
---------------
```
Usage: checkSlotsGui.py [--help] [--noChromeCast]
```

1. In the GUI, you will need to enter your Store Location string.

    i. Go to https://www.loblaws.ca/store-locator
    
    ii. Choose a location and click the "Location Details" link
    
    iii. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)
    
   The 4 digit string at the end of this URL must be entered into the Store Location box in the GUI.
   If you want your store location to always be the default when you start the GUI, adjust the "DEFAULT_STORE=1007" line in checkSlotsGui.py.

2. To poll your store periodically and show latest results, check the "Poll fo Openings" checkbox.  The frequency of checks is controlled with the "Check frequency (seconds):" entry.  The "Check Now" button (at any time) will cause an immediate check of the store.

3. Periodic polling needs to be restarted after any change to "Store Type".

4. If you want any change in the earliest timeslot to be announced on a Chromecast device (e.g. GoogleHome), click the "Start Server" button (this only needs to be done once), select the device with the "Broadcast Device" drop-down, and make sure the "Broadcast?" checkbox is checked.  These can be adjusted at any time, and the current values will be used at the next Check time.

5. Clicking the "Refresh Devices" at any time will refresh the list of available Chromecast devices.

6. Technical detail: the "Start Server" button starts up an HTTP server in a subdirectory "audio" of the directory containing the checkSlotsGui.py script.  If you want to start such a server manually in some other location, you do need to tell the GUI where the root of this server is with the "Chromecast Server Directory". The GUI will put the announcements into this directory for ChromeCast and then broadcast the announcement file to the chromecast devices.  Once you have a server running (either by pressing the "Start Server" button or starting a server in a separate console), you can test the Broadcast capabilities with the "Test" button, which will broadcast "Hello World" to the selected Broadcast device.
    
7. If you don't have any ChromeCast devices and want to prevent the GUI from even checking for ChromeCast devices, use the --noChromeCast startup option.  If you do this, you do not need to install the pychromecast and gtts libraries: 
    ```
    python .\checkSlotsGui.py --noChromeCast
    ```
    
8. Technical detail: The Loblaws sites seem to keep their time-points in Universal Cordinated Time (UCT or GMT).  To display them in local time, they need to be adjusted via the TimeZoneOffset.  The default TimeZoneOffset is set up for Eastern Daylight Time.

History
-------
Based on "groceryslots" (check_slots.py) by Jeffrey Wintersinger https://github.com/jwintersinger/groceryslots. Other Loblaws family sites contributed by Daniel McIntosh.
