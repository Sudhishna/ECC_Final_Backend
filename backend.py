import jinja2
import json
import os
import threading
from time import sleep
import subprocess
from threading import Timer
import time
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import re

campus_info = {"campuses":[{"leaf":1, "spine":1}]}
'''
ports_map = { "1" => [1,2,3],
              "2" => [3,4,5],
              "3" => [1,4],
              "4" => [2,5]}
'''

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def per_campus(start,end,leaf,spine):
  links = leaf * spine
  total = leaf + spine

  dict = []
  for num in range(1,spine+1):
    spine_id = num
    spine_ports = range(num+start, links+1+start, spine)
    end_list = []
    end_list.append(end)
    if num % 2 == 0 and num != spine:
      end += 1
      end_list.append(end)
    spine_ports.extend(end_list)
    #dict.update({spine_id:spine_ports})
    dict.append(spine_ports)

  l_ports = list(chunks(range(1+start, links+1+start), spine))
  for num,ports in enumerate(l_ports):
    leaf_id = num + 1 + spine
    leaf_ports = ports
    #dict.update({leaf_id:leaf_ports})
    dict.append(leaf_ports)


  return dict

def between_spines(start,end,spine1,spine2):
  links = spine1 * spine2
  total = spine1 + spine2

  dict = []
  for num in range(1,spine+1):
    #spine_id = num
    spine_ports = range(num+start, links+1+start, spine)
    dict.append(spine_ports)

  l_ports = list(chunks(range(1+start, links+1+start), spine))
  for num,ports in enumerate(l_ports):
    leaf_id = num + 1 + spine
    leaf_ports = ports
    dict.append(leaf_ports)

  return dict

ports_map = {}

start = 0
end = 0
ports = []
for campus in campus_info["campuses"]:
  leaf = campus["leaf"]
  spine = campus["spine"]
  total = leaf * spine
  end += total
  ports.extend(per_campus(start,end+1,leaf,spine))
  start +=  total + spine - 1
  end += spine - 1

dev_num = 1
for port in ports:
  ports_map.update({dev_num:port})
  dev_num += 1

spine_list = []
couter = 1
for campus in campus_info["campuses"]:
  spine_list.append(campus["spine"])


counter = 1
spine_lst = []
spine_ports = []
for index,spine in enumerate(spine_list):
  if counter != len(campus_info["campuses"]):
    spine1 = spine_list[index]
    spine2 = spine_list[index+1]
    total = spine1 * spine2
    end += total
    ports1 = between_spines(start,end,spine1,spine2)
    spine_ports.extend(ports1)
    start += total
  counter += 1


spine_id_list = []
spine_counter = 0
spine_count = 0
name_list = []
for index,campus in enumerate(campus_info["campuses"]):
  leaf = campus["leaf"]
  spine = campus["spine"]
  total = leaf + spine
  spine_id_lst = []
  for num in range(spine_counter+1,spine + spine_counter + 1,1):
    spine_counter = num
    name_list.append("spine")
    spine_id_lst.append(spine_counter)
  spine_id_list.extend(spine_id_lst)
  spine_count += 1
  if spine_count % 2 == 0 and spine_count != len(campus_info["campuses"]):
    spine_id_list.extend(spine_id_lst)
  spine_counter += leaf
  for name in range(leaf):
    name_list.append("leaf")


for spine_id,spine_port in zip(spine_id_list,spine_ports):
  ports_map[spine_id].extend(spine_port)

portsMap = ""
for ports in ports_map:
  print ports_map[ports]
  if ports == 1:
    #portsMap = '{"' + str(ports) + '"' + '=>' + str(ports_map[ports])
    portsMap = str(ports) + ":" + str(ports_map[ports])
  else:
    portsMap = portsMap + "*" + str(ports) + ":" + str(ports_map[ports])
    #portsMap = portsMap + ',' + '"' + str(ports) + '"' + '=>' + str(ports_map[ports])

print portsMap



#leaf = 2
#spine = 2

total= len(name_list)
print(total)

inventory_file = "inventory/inventory"
open(inventory_file, 'w').close()

#f = open('sample.json', 'w')
#f.close()

def spinvm(number,dev_name):
    # Sleeps a random 1 to 10 seconds
    # rand_int_var = randint(1, 10)
    print "++++++++++" + str(number) + "**************"
    subprocess.call(['vagrant','--vqfx-id=%s' % str(number),'--ports-map=%s' % portsMap,'--dev-name=%s' % dev_name,'up'])
    print "Thread " + str(number) +"completed spinup"

thread_list = []

for i,name in zip(range(1, total+1),name_list):
    print i,name
    # Instantiates the thread
    # (i) does not make a sequence, so (i,name)
    t = threading.Timer(3.0,spinvm, args=(i,name))              
    # Sticks the thread in a list so that it remains accessible
    thread_list.append(t)

# Starts threads
for thread in thread_list:
    thread.start()
    time.sleep(10)

# This blocks the calling thread until the thread whose join() method is called is terminated.
# From http://docs.python.org/2/library/threading.html#thread-objects
for thread in thread_list:
    thread.join()

# Demonstrates that the main process waited for threads to complete
print "Done creating vms"

vqfxDict = {}

with open('inventory/inventory', 'r') as f:
    for line in f:
        vqfx = line.split(" ",1)[0]
        if "vqfx" in vqfx and "pfe" not in vqfx:
            vqfxDict[vqfx] = {}
            m = re.search('\w*.*ansible_host=(\w*.*?) ',line)
            host = m.group(1)
            vqfxDict[vqfx]['host'] = host
            m = re.search('\w*.*ansible_port=(\w*.*?) ',line)
            port = m.group(1)
            vqfxDict[vqfx]['port'] = port
print vqfxDict

for key,value in vqfxDict.iteritems():
    print "\n#####  Configuring: " + key + " #####\n"
    print "host " + value['host']
    print "port " + value['port']

    dev = Device(host=value['host'], user='root', password='Juniper',port=value['port'])
    dev.open()
    pprint(dev.facts)

    cu = Config(dev)
    cmd = "set system host-name " + key
    cu.load(cmd, format='set')
    cu.commit()

    dev.close()

