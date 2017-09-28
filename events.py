#!/usr/bin/python

import requests
import XenAPI
import sys

session = XenAPI.Session("")
session.login_with_password("","")
session.xenapi.event.register(["VM"]) # register for events in the pool and VM objects 

vm_power_states = {}

url = "http://localhost:5000/api/cc/CMXS9/power-state-changed"

while True:
  try:
    events = session.xenapi.event.next() # block until a xapi event on a xapi DB object is available
    for event in events:
      if event['class'] == 'vm' and event['operation'] == 'mod':
        vm = event['snapshot']
        vm_name = vm['name_label']
        vm_power = vm['power_state']
        
        if vm_name not in vm_power_states or vm_power_states[vm_name] != vm_power:
          print("%s power state changed to %s" % (vm_name, vm_power))
          vm_power_states[vm_name] = vm_power

          payload = {'VM': vm_name, 'power_state': vm_power}
          requests.post(url, json=payload)
        
  except XenAPI.Failure as e:
    if len(e.details) > 0 and e.details[0] == 'EVENTS_LOST':
      session.xenapi.event.unregister(["VM","pool"])
      session.xenapi.event.register(["VM","pool"])
    session.xenapi.logout()