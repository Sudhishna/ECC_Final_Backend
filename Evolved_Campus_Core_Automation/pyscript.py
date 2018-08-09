import time
import re
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from campus_config import Campus_Config

campus_config = Campus_Config()

file_name = "/home/ubuntu/Evolved_Campus_Core_Automation/Inventory"

with open(file_name) as f:
    content = f.read()
    campuses = re.findall('\[(.*?)\]',content)

leaf = []
spine = []
for campus in campuses:
    if not "children"in campus:
        if "leaf" in campus:
            data_loader = DataLoader()
            inventory = InventoryManager(loader = data_loader,
                                         sources=[file_name])
            leaf.extend(inventory.get_groups_dict()[campus])
        elif "spine" in campus:
            data_loader = DataLoader()
            inventory = InventoryManager(loader = data_loader,
                                         sources=[file_name])
            spine.extend(inventory.get_groups_dict()[campus])

for campus in campuses:
    if "children"in campus:
        campus_id = campus.split(":")[0]
        print campus_id
        data_loader = DataLoader()
        inventory = InventoryManager(loader = data_loader,
                                     sources=[file_name])
        dev_ips = inventory.get_groups_dict()[campus_id]

        dev = campus_config.enable_lldp(spine) 

print "Please wait for the devices to establish the links...."
time.sleep(45)

dev = campus_config.campus_underlay(dev_ips,spine)

#for campus in campuses:
#    if "children"in campus:
#        campus_id = campus.split(":")[0]
#        print campus_id
#        data_loader = DataLoader()
#        inventory = InventoryManager(loader = data_loader,
#                                     sources=[file_name])
#        dev_ips = inventory.get_groups_dict()[campus_id]
#
#        dev = campus_config.campus_underlay(dev_ips,spine)

#print leaf
