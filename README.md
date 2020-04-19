Grocery Slots
=============
This program will periodically check Loblaws or Superstore for open grocery pick-up slots (by default, every 60 seconds), printing open slots to the terminal. The program can also announce via any Chromecast-compatible device (including Google Home) when a new spot opens.

checkSlotsGui.py is a self-contained GUI that does not require any options.

Requirements
------------
* Python 3

Usage
-----
1. Install necessary Python libraries.

    ```
    pip3 install --user requests python-dateutil
    ```

2. Find your Loblaws location ID.
    1. Go to https://www.loblaws.ca/store-locator
    2. Choose a location and click the "Location Details" link
    3. Find the integer ID at the end of the URL (e.g., `1007` from https://www.loblaws.ca/store-locator/details/1007)

3. Run the main script.

    ```
    python3 check_slots.py --location 1007
    ```
    
GUI usage
---------
1. Install necessary Python libraries.

    ```
    pip3 install --user requests python-dateutil
    ```
2. Run the script:
    python .\checkSlotsGui.py
    
3. If you don't have any ChromeCast devices, 
    python .\checkSlotsGui.py --noChromeCast


Getting audible announcements
-----------------------------
You can configure the script to announce new slots via any Chromecast device (including Google Home).

1. Install additional libraries.

    ```
    pip3 install --user pychromecast gtts
    ```

2. In a separate terminal, start a web server to serve the text-to-speech audio
   file to your Chromecast device. By default, this audio file will be stored
   as `/tmp/out.mp3`, but you can control this via the `AUDIO_PATH` variable in
   `saytext.py`.

    ```
    cd /tmp
    python3 -m http.server
    ```

3. Change the `HTTP_IP` variable in `saytext.py` to correspond to the IP of
   your local machine that will serve the audio file to your Chromecast.

4. Run the main script with `--announce`.

    ```
    python3 check_slots.py --location 1007 --announce
    ```

Usage reference
---------------
```
usage: check_slots.py [-h] [--location LOCATION] [--delay DELAY] [--tzoffset TZOFFSET] [--announce] [--site {loblaws,superstore}]

Query PC-umbrella grocery store (Loblaws, Superstore, etc.) for open pick-up slots

optional arguments:
  -h, --help            show this help message and exit
  --location LOCATION   Integer ID of PC-umbrella (Loblaws, Superstore, etc.) grocery store (default: 1007)
  --delay DELAY         Delay ins econds between checks (default: 60)
  --tzoffset TZOFFSET   Timezone offset in hours. Default seems to work for both Toronto and Calgary (default: 4)
  --announce            Announce new open slots via Chromecast device (including Google home (default: False)
  --site {loblaws,superstore}
                        Type of PC-umbrella grocery store (default: loblaws)
```
