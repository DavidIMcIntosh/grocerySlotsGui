#required installs:
#pip3 install --user requests python-dateutil  pychromecast gtts
import requests
import dateutil.parser
import datetime
import time
import threading
import argparse
import sys
import re
import tkinter as tk
import pychromecast
import gtts
import os
import socket
import subprocess

DEFAULT_STORE=1021
DEFAULT_TYPE='loblaws'

SITES = [ 'loblaws', 'superstore', 'valumart', 'nofrills', 'zehrs']
DOMAINS = {
  'superstore': 'www.realcanadiansuperstore.ca',
  'loblaws': 'www.loblaws.ca',
  'valumart': 'www.valumart.ca',
  'nofrills': 'www.nofrills.ca',
  'zehrs': 'www.zehrs.ca',
}
SITE_BANNERS = {
  'superstore': 'superstore',
  'loblaws': 'loblaw',
  'valumart': 'valumart',
  'nofrills': 'nofrills',
  'zehrs': 'zehrs',
}


AUDIO_SERVER_SUBDIR = 'audio'
def getServerAudioDir():
  return os.path.join(os.getcwd(), AUDIO_SERVER_SUBDIR)

def startServer(drct):
  if not os.path.exists(drct):
    os.mkdir(drct)
  cmdArgs = ['python', '-m', 'http.server']
  return subprocess.Popen(cmdArgs, cwd = drct, creationflags = subprocess.CREATE_NEW_CONSOLE)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class sayText:
  def __init__(self, serverDir, HttpIp, HttpPort=8000):
    self.serverDir = serverDir
    self.HTTP_IP = HttpIp
    self.HTTP_PORT = HttpPort
  def getChromeCastDevices():
    cc = pychromecast.get_chromecasts()
    devices = []
    for C in cc:
      devices.append(C.device.friendly_name)
    return devices
  def say(self, text, device, tag): #, volume=1.0):
    now = datetime.datetime.now()
    mp3File = '/%s_%s.mp3' % (tag, now.strftime('%Y-%m-%d_%H.%M.%S'))
    audio_path = '%s%s' % (self.serverDir,mp3File)
    speech = gtts.gTTS(text = text, lang = 'en', slow = False)
    speech.save(audio_path)
    cc = pychromecast.get_chromecasts()
    cast = next(C for C in cc if C.device.friendly_name == device)
    #cast.wait()
    #cast.set_volume(volume)
    cast.wait()
    mc = cast.media_controller
    mc.play_media('http://%s:%s%s' % (self.HTTP_IP, self.HTTP_PORT, mp3File), 'audio/mp3')
    mc.block_until_active()
    time.sleep(10)
    os.remove(audio_path)

def make_header(site):
  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en' ,
    'Site-Banner': SITE_BANNERS[site],
    'Content-Type': 'application/json;charset=utf-8',
    'Connection': 'keep-alive',
   }
  return headers

def fetch(site, location, cookies):
  r = requests.get('https://%s/api/pickup-locations/%s/time-slots' % (DOMAINS[site], location), cookies=cookies, headers=make_header(site))
  if r==None or r=='' :
    return ''
  return r.json()

def get_cookies(site):
  r = requests.get('https://%s' % DOMAINS[site], headers=make_header(site))
  return r.cookies

def parse_time(T, offset):
  T = dateutil.parser.parse(T, fuzzy=True)
  # Account for timezone difference
  T -= datetime.timedelta(hours=offset)
  return T

def check_slots(site, location, cookies, tzoffset=4):
  response = fetch(site, location, cookies)
  avail = [(
    parse_time(S['startTime'], tzoffset),
    parse_time(S['endTime'], tzoffset),
  ) for S in response['timeSlots'] if S['available']]
  return [S[0] for S in avail]

class MyGui:
  def __init__(self, parent, noChromeCast):
    self.gui = parent
    self.gui.title('Grocery Pickup Slots')
    rw=0
    msg = [ 'To find the "Store Location":'
          , '1. Go to https://www.loblaws.ca/store-locator'
          , '2. Choose a location and click the "Location Details" link'
          , '3. Find the integer ID at the end of the URL (e.g., https://www.loblaws.ca/store-locator/details/%s)' % DEFAULT_STORE
          ]
    nRows = len(msg)+1
    msgText = '\n'.join(msg)
    self.instructions = tk.Message(self.gui, text=msgText, width=300)
    self.instructions.grid(row=rw, column=0, columnspan=2, rowspan=nRows, sticky='NESW')
    rw += nRows
    self.label2 = tk.Label(self.gui, text='Store Location #:')
    self.label2.grid(row=rw, column=0, sticky=tk.E)
    self.location = tk.Entry(self.gui, width=5)#store #
    self.location.grid(row=rw, column=1, sticky=tk.W)
    self.location.insert(0, DEFAULT_STORE)
    rw += 1
    self.label3 = tk.Label(self.gui, text='Check Frequency (seconds):')
    self.label3.grid(row=rw, column=0, sticky=tk.E)
    self.delay = tk.Entry(self.gui, width=5)#poll frequency
    self.delay.grid(row=rw, column=1, sticky=tk.W)
    self.delay.insert(0,'300')
    rw += 1
    self.label4 = tk.Label(self.gui, text='TimeZone offset:')
    self.label4.grid(row=rw, column=0, sticky=tk.E)
    self.tzoffset = tk.Entry(self.gui, width=3)
    self.tzoffset.grid(row=rw, column=1, sticky=tk.W)
    self.tzoffset.insert(0,'4')
    rw += 1
    self.label6 = tk.Label(self.gui, text='Store type:')
    self.label6.grid(row=rw, column=0, sticky=tk.E)
    self.site = tk.StringVar(self.gui)
    self.site.set(DEFAULT_TYPE)
    self.siteSelector = tk.OptionMenu(self.gui, self.site, *SITES )
    self.siteSelector.grid(row=rw, column=1, sticky=tk.W)
    rw += 1
    self.announce = tk.IntVar()
    if noChromeCast:
      chromeCastState = 'disabled'
      self.announce.set(0)
      self.DEVICES = []
    else:
      chromeCastState = 'normal'
      self.announce.set(1)
      self.DEVICES = sayText.getChromeCastDevices()
    self.device = tk.StringVar(self.gui)
    if len(self.DEVICES)==0 :
      castState = 'disabled'
      self.DEVICES.append('noChromeCast')
    else:
      castState = 'normal'

    self.device.set(self.DEVICES[0])
    self.announceW = tk.Checkbutton(self.gui, text='Broadcast?', state=castState, variable=self.announce)#turn on broadcast
    self.announceW.grid(row=rw, column=0)
    self.testcastbutton = tk.Button(self.gui, text='Test', state=castState, command=self.testcast) #test broadcast
    self.testcastbutton.grid(row=rw, column=1, sticky=tk.W)
    rw += 1
    self.label5 = tk.Label(self.gui, text='Broadcast device:', state=castState)
    self.label5.grid(row=rw, column=0)
    self.refreshDevicesButton = tk.Button(self.gui, text='Refresh Devices', state=chromeCastState, command=self.refreshDevices)
    self.refreshDevicesButton.grid(row=rw, column=1, sticky=tk.W)
    rw += 1
    self.deviceSelector = tk.OptionMenu(self.gui, self.device, *self.DEVICES )
    self.deviceSelector.config(state=castState)
    self.deviceSelector.grid(row=rw, column=0, columnspan=2)
    rw += 1
    self.label1 = tk.Label(self.gui, text='Chromecast Server Directory', state=castState)
    self.label1.grid(row=rw, column=0)
    self.startServerbutton = tk.Button(self.gui, text='Start Server', state=castState, command=self.startServer) #test broadcast
    self.startServerbutton.grid(row=rw, column=1, sticky=tk.W)
    rw += 1
    dir = getServerAudioDir()
    self.serverDir = tk.Entry(self.gui, width=len(dir)+4)
    self.serverDir.grid(row=rw, column=0, columnspan=2)
    self.serverDir.insert(0, dir )
    self.serverDir.config(state=castState)
    rw += 1
    self.label7 = tk.Label(self.gui, text='Chromecast Server IP', state=castState)
    self.label7.grid(row=rw, column=0, sticky=tk.E)
    self.serverIP = tk.Entry(self.gui, width=15)
    self.serverIP.grid(row=rw, column=1, sticky=tk.W)
    self.serverIP.insert(0,get_ip())
    self.serverIP.config(state=castState)
    rw += 2
    self.pollButton = tk.IntVar()
    self.pollButtonW = tk.Checkbutton(self.gui, text='Poll for Openings', variable=self.pollButton, command=self.startpoll)#turn on broadcast
    self.pollButtonW.grid(row=rw, column=0, columnspan=2)
    rw += 1
    self.checkNowButton = tk.Button(self.gui, text='Check Now', command=self.doCheckNow)
    self.checkNowButton.grid(row=rw, column=0, columnspan=2)
    rwspan = 24
    self.labelLast = tk.Label(self.gui, text='No check run yet')
    self.labelLast.grid(row=0, column=2)
    self.labelNext = tk.Label(self.gui, text='Next check unscheduled')
    self.labelNext.grid(row=1, column=2)
    self.labelAvailable = tk.Label(self.gui, text='Available time slots:')
    self.labelAvailable.grid(row=2, column=2)
    self.message = tk.Text(self.gui, width=30) #,text='')
    self.scrollb = tk.Scrollbar(self.gui, command=self.message.yview, orient=tk.VERTICAL)
    self.scrollb.grid(row=3, column=3, rowspan=rwspan, sticky='ns') 
    self.message.config(yscrollcommand=self.scrollb.set)
    self.message.grid(row=3, column=2, rowspan=rwspan)
    self.site.trace("w", self.siteChanged)
    self.init_cookies = None
    self.prev_first_slot = None
    self.scheduledId = None
  def testcast(self):
    self.say('Hello World')
  def refreshDevices(self):
    self.DEVICES = sayText.getChromeCastDevices()
    menu = self.deviceSelector['menu']
    menu.delete(0, 'end')
    current = self.device.get()
    if current != None and  current != '':
      menu.add_command(label=current, command=tk._setit(self.device, current))
    for choice in self.DEVICES:
      if choice != current:
        menu.add_command(label=choice, command=tk._setit(self.device, choice))
    if len(self.DEVICES)==0 :
      castState = 'disabled'
    else:
      castState = 'normal'
    self.announceW.config(state=castState)
    self.testcastbutton.config(state=castState) #test broadcast
    self.label5.config(state=castState)
    self.deviceSelector.config(state=castState)
    self.label1.config(state=castState)
    self.startServerbutton.config(state=castState) #test broadcast
    self.serverDir.config(state=castState)
    self.label7.config(state=castState)
    self.serverIP.config(state=castState)
  def doCheckNow(self):
    if self.pollButton.get() == 0:
      self.init_cookies = get_cookies(self.site.get())
    self.doCheck()
  def doCheck(self):
    site = self.site.get()
    location = self.location.get()
    slots = check_slots(site, location, self.init_cookies, int(self.tzoffset.get()))
    if self.announce.get()!=0 and len(slots) > 0 and slots[0] != self.prev_first_slot:
      saytime = slots[0].strftime('%A, %B %d at %I %p')
      if site=='superstore':
        saystore='at Super-Store %s' % location
      else:
        saystore='at %s store %s' % (site, location)
      txt = 'The next available grocery pickup slot %s is on %s.' % (saystore, saytime)
      self.say(txt)
      self.prev_first_slot = slots[0]
    now = datetime.datetime.now()
    self.labelLast.config(text='Last checked at %s' % now.strftime('%H:%M:%S (%Y-%m-%d)'))
    out=[]
    for S in slots:
      out.append('avail = %s' % S.strftime('%Y-%m-%d %H:%M'))
    txt = '\n'.join(out) + '\n'
    self.message.config(state=tk.NORMAL)
    self.message.delete(1.0, tk.END)
    self.message.insert(tk.END, txt)
    self.message.config(state=tk.DISABLED)
    self.labelAvailable.config(text='Available time slots (store# %s):' % self.location.get())
  def say(self, txt):
    saytext = sayText(self.serverDir.get(), self.serverIP.get())
    saytext.say(txt, self.device.get(), 'out')
  def startServer(self):
    startServer(self.serverDir.get())
  def doCheckPeriodic(self):
    if self.pollButton.get() == 1:
      self.doCheck()
      dly = int(self.delay.get())
      now = datetime.datetime.now()
      self.labelNext.config(text='Next check at %s' % (now + datetime.timedelta(seconds=dly)).strftime('%H:%M:%S (%Y-%m-%d)'))
      self.scheduledId = self.gui.after(dly*1000, self.doCheckPeriodic)
  def startpoll(self):
    if self.pollButton.get() == 1:
      self.init_cookies = get_cookies(self.site.get())
      self.doCheckPeriodic()
    else:
      self.unschedule()
  def unschedule(self):
    self.pollButton.set(0)
    self.labelNext.config(text='Next check unscheduled')
    if self.scheduledId != None:
      self.gui.after_cancel(self.scheduledId)
      self.scheduledId=None
  def siteChanged(self, n, m, x):
    self.unschedule()

def main():
  parser = argparse.ArgumentParser(
    description='Query PC-umbrella grocery store (Loblaws, Superstore, etc.) for open pick-up slots',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument('--noChromeCast', action='store_true',
    help='No chromecast available')
  args = parser.parse_args()
  gui = tk.Tk()
  app = MyGui(gui, args.noChromeCast)
  gui.mainloop()

if __name__ == '__main__':
  main()
