from helpers import Helpers
from jnpr.junos.utils.config import Config
import re
import random
import math
import os
import jinja2
import time
from ipcalculator import IPCalculator
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import LockError
from jnpr.junos.exception import UnlockError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError


"""
Keeping this script simple by calling the functions written in the helper module
"""

helpers = Helpers()

vqfxDict = {}
hosts_dict = {}
link_layer_list = list()
link_layer_map = {} 
bgp_detail = {}
route_list = {}

hosts_dict = {'vqfx2': {'interfaces': [{'ip_address': '192.168.210.30/30', 'physical_interface': 'xe-0/0/2', 'description': 'to_vqfx1'}, {'ip_address': '192.168.210.245/30', 'physical_interface': 'xe-0/0/4', 'description': 'to_vqfx6'}, {'ip_address': '192.168.210.41/30', 'physical_interface': 'xe-0/0/3', 'description': 'to_vqfx5'}], 'route_filter': [], 'overlay_peers': [], 'bgp': [{'remote_peer': '192.168.210.29', 'remote_as': 115, 'remote_description': 'vqfx1'}, {'remote_peer': '192.168.210.246', 'remote_as': 153, 'remote_description': 'vqfx6'}, {'remote_peer': '192.168.210.42', 'remote_as': 113, 'remote_description': 'vqfx5'}], 'bgpasn': 152, 'bgp_router_id': '10.0.0.57'}, 'vqfx1': {'interfaces': [{'ip_address': '192.168.210.29/30', 'physical_interface': 'xe-0/0/2', 'description': 'to_vqfx2'}, {'ip_address': '192.168.210.221/30', 'physical_interface': 'xe-0/0/4', 'description': 'to_vqfx6'}, {'ip_address': '192.168.210.229/30', 'physical_interface': 'xe-0/0/3', 'description': 'to_vqfx5'}], 'route_filter': [], 'overlay_peers': [], 'bgp': [{'remote_peer': '192.168.210.30', 'remote_as': 152, 'remote_description': 'vqfx2'}, {'remote_peer': '192.168.210.222', 'remote_as': 153, 'remote_description': 'vqfx6'}, {'remote_peer': '192.168.210.230', 'remote_as': 113, 'remote_description': 'vqfx5'}], 'bgpasn': 115, 'bgp_router_id': '10.0.0.64'}, 'vqfx6': {'interfaces': [{'ip_address': '192.168.210.222/30', 'physical_interface': 'xe-0/0/3', 'description': 'to_vqfx1'}, {'ip_address': '192.168.210.246/30', 'physical_interface': 'xe-0/0/4', 'description': 'to_vqfx2'}, {'ip_address': '192.168.210.210/30', 'physical_interface': 'xe-0/0/2', 'description': 'to_vqfx5'}], 'route_filter': [], 'overlay_peers': [], 'bgp': [{'remote_peer': '192.168.210.221', 'remote_as': 115, 'remote_description': 'vqfx1'}, {'remote_peer': '192.168.210.245', 'remote_as': 152, 'remote_description': 'vqfx2'}, {'remote_peer': '192.168.210.209', 'remote_as': 113, 'remote_description': 'vqfx5'}], 'bgpasn': 153, 'bgp_router_id': '10.0.0.48'}, 'vqfx5': {'interfaces': [{'ip_address': '192.168.210.230/30', 'physical_interface': 'xe-0/0/3', 'description': 'to_vqfx1'}, {'ip_address': '192.168.210.42/30', 'physical_interface': 'xe-0/0/4', 'description': 'to_vqfx2'}, {'ip_address': '192.168.210.209/30', 'physical_interface': 'xe-0/0/2', 'description': 'to_vqfx6'}], 'route_filter': [], 'overlay_peers': [], 'bgp': [{'remote_peer': '192.168.210.229', 'remote_as': 115, 'remote_description': 'vqfx1'}, {'remote_peer': '192.168.210.41', 'remote_as': 152, 'remote_description': 'vqfx2'}, {'remote_peer': '192.168.210.210', 'remote_as': 153, 'remote_description': 'vqfx6'}], 'bgpasn': 113, 'bgp_router_id': '10.0.0.78'}}

for key,values in hosts_dict.iteritems():
    hostname = key
    filter_list = list()
    for key,vals in values.iteritems():
        if key == "bgp":
            for val in vals:
                bgp_remote_host = val["remote_description"]
                print bgp_remote_host
                print hosts_dict[bgp_remote_host]["bgp_router_id"]
                filter_list.append(hosts_dict[bgp_remote_host]["bgp_router_id"])
    for filter in filter_list:
        values['overlay_peers'].append(filter)
print hosts_dict

