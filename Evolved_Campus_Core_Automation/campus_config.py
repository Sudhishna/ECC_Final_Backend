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
class Campus_Config:

    def enable_lldp(self, spine_ips):
        helpers = Helpers()
        for spine_ip in spine_ips:
            # Access the device using pyez netconf and fetch Serial Number
            print "Connecting to the device....\n"
            dev = helpers.device_connect(spine_ip)
            dev.open()
            on_box_hostname = dev.facts["hostname"]

            print "\n#####  Configuring: " + on_box_hostname + " #####\n"
            print "Configuring Below Device " + on_box_hostname + "\nHost IP: " + spine_ip + "\n"

            # Clear the previous configs if any
            with Config(dev, mode='private') as cu:
                del_config = """
                             delete protocols bgp
                             delete protocols evpn
                             delete protocols lldp
                             delete routing-options
                             delete vlans
                             delete switch-options
                             delete policy-options
                             delete interfaces lo0
                             delete interfaces ae1
                             delete interfaces ae2
                             delete routing-instances  
                             delete chassis
                             """
                cu.load(del_config, format='set',ignore_warning=True)
                cu.pdiff()
                cu.commit()

            on_box_serialnumber = dev.facts["serialnumber"]
            on_box_version = dev.facts["version"]
            on_box_model = dev.facts["model"]
            print " On Box Serialnumber: " + on_box_serialnumber + "\n On Box Version: " + on_box_version + "\n On Box Model: " + on_box_model + "\n"

            # Push the new CONFIG Required
            print("\n\nLLDP protocol is configured in the devices")
            cfg = helpers.load_config(on_box_model, "basic", dev)

            dev.close()

    def campus_underlay(self, device_ips, spine_ips):
	helpers = Helpers()

	vqfxDict = {}
	hosts_dict = {}
	link_layer_list = list()
	link_layer_map = {} 
	bgp_detail = {}

        for spine_ip in spine_ips:
            '''
            BGP INFORMATION FETCHED
            IP IS NONE. WILL BE ASSIGNED LATER
            '''
	    dev = helpers.device_connect(spine_ip)
            dev.open()
	
	    on_box_hostname = dev.facts["hostname"]
            bgpasn = helpers.fetch_value("bgpasn",1)
            bgp_detail.update({on_box_hostname: {'bgpasn': bgpasn}})

	    dev.close()
        print list(bgp_detail.keys())

        for spine_ip in spine_ips:
            # Access the device using pyez netconf and fetch Serial Number
            dev = helpers.device_connect(spine_ip)
            dev.open()
	    on_box_hostname = dev.facts["hostname"]
		
            # Fetch the link layer information
            interfaces = list() 
            remote_connections = list()
            ints_list = list()
            bgp_list = list()
            interfaces_dict = {}

            print "Fetching LINK LAYER CONNECTIVITY INFORMATION"
            cli_lldp = dev.rpc.get_lldp_neighbors_information()

            print "links"
            for lldp in cli_lldp.findall("lldp-neighbor-information"):
                '''
                LINK LAYER CONNECTIVITY INFORMATION APPENDED
                '''
    	        local_port = lldp.findtext("lldp-local-interface") 
	        if local_port is None:
	            local_port = lldp.findtext("lldp-local-port-id")
	            local_port = local_port
    	        else:
	            local_port = local_port.split(".")
	            local_port = local_port[0]

                with Config(dev, mode='private') as cu:  
                    del_interface = "delete interfaces " + local_port + " unit 0 family inet"
                    cu.load(del_interface, format='set',ignore_warning=True)
                    cu.pdiff()
                    cu.commit()

	        remote_chassis = lldp.findtext("lldp-remote-chassis-id")
	        remote_system = lldp.findtext("lldp-remote-system-name")
                print on_box_hostname + "**" + remote_system

                if remote_system in list(set(bgp_detail.keys())) :
                    interfaces.append(local_port)

	            remote_connections.append(remote_system)
	            remote_port = lldp.findtext("lldp-remote-port-description")
                    remote_port = remote_port.split(".")
                    remote_port = remote_port[0]
                    link_layer_list.append({'local_system': on_box_hostname, 'local_port': local_port, 'local_ip': 'None', 'remote_ip': 'None', 'remote_system': remote_system, 'remote_port': remote_port, 'broadcast': 'None'})

                    '''
                    INTERFACES INFORMATION FETCHED 
	            IP IS NONE. WILL BE ASSIGNED LATER
                    '''
                    print "Fetching INTERFACES INFORMATION"
    	            description = "to_" + remote_system
	            local_port = local_port.strip()
                    description = description.strip()
	            ints_list.append({'physical_interface': local_port, 'description': description, 'ip_address': "None" })

            '''
            BGP INFORMATION FETCHED 
            IP IS NONE. WILL BE ASSIGNED LATER
            '''
            print "Fetching BGP INFORMATION"
            local_as = bgp_detail[on_box_hostname]["bgpasn"]
            bgp_router_id = helpers.fetch_value("bgp_router_id",1)

            for remote_connection in remote_connections:
                print remote_connection
                print bgp_detail 
                remote_as = bgp_detail[remote_connection]["bgpasn"]
                print remote_as
                bgp_list.append({ 'remote_as': remote_as, 'remote_peer': 'None', 'remote_description' : remote_connection })

            '''
            INTERFACES,BGP,BGP_ROUTER_ID,BGPASN,ROUTER_FILTER
            INFORMATION APPENDED
            IPs ARE NONE. WILL BE ASSIGNED LATER
            '''
            interfaces_dict.update({on_box_hostname: {'interfaces': ints_list,'bgp_router_id': bgp_router_id,'bgpasn': local_as,'bgp': bgp_list,'route_filter': [],'overlay_peers': [],'vlans': [10,20,30,40]}})

            hosts_dict.update(interfaces_dict)
            dev.close()

        '''
        LINK LAYER MAP:
        LINK INFO: LOCAL(PORT,IP,HOST) & REMOTE(PORT,IP,HOST)
        REMOVE DUPLICATES: DUPLICATES EXIST BCOS SAME LINK INFO FOUND IN BOTH LOCAL AND REMOTE HOST
        '''
        print "Creating LINK LAYER MAP: LOCAL(PORT,IP,HOST) & REMOTE(PORT,IP,HOST)"
        link_layer_map.update({'link_layer': link_layer_list})
        links = link_layer_map["link_layer"]
        for link in links:
            for rlink in links:
                if link["local_system"]+link["local_port"] == rlink["remote_system"]+rlink["remote_port"]:
                    if link["remote_system"]+link["remote_port"] == rlink["local_system"]+rlink["local_port"]:
	        	    links.remove(rlink)

        '''
        GENERATE IPS FOR CONNECTED INTERFACES 
        BASED ON:
        IP START & IP END, NETMASK, ALREADY USED IP
        '''
        print "GENERATE IPS FOR CONNECTED INTERFACES BASED ON: IP START & IP END, NETMASK, ALREADY USED IP"
        for link in links:
            interface_ip = helpers.fetch_value("interface_ip",1)
            print "return value"
            print interface_ip

            ip = IPCalculator(interface_ip)
            ip_detail = ip.__repr__()
            hostrange = ip_detail["hostrange"]
            hostrange = hostrange.split("-")
            broadcast = ip_detail["broadcast"]
            cidr = ip_detail["cidr"]

            link['local_ip'] = hostrange[0]+"/"+str(cidr)
            print "local_ip"
            print link['local_ip']
            link['remote_ip'] = hostrange[1]+"/"+str(cidr)
            print "remote_ip"
            print link['remote_ip']
            link['broadcast'] = broadcast+"/"+str(cidr)
            print "broadcast"
            print link['broadcast']

        '''
        ASSIGN THE GENERATED IPs TO THE INTERFACES CONFIG
        '''
        print "ASSIGN THE GENERATED IPs TO THE INTERFACES CONFIG"
        for key, vals in hosts_dict.iteritems():
            hostname = key
            for key,vals in vals.iteritems():
    	        if key == "interfaces":
	            for val in vals:
	                interface = val["physical_interface"]
	    	        for link in links:
		            if hostname == link["local_system"] and interface == link["local_port"]:
		    	        val["ip_address"] = link["local_ip"]
		            elif hostname == link["remote_system"] and interface == link["remote_port"]:
			        val["ip_address"] = link["remote_ip"]


        '''
        ASSIGN THE GENERATED IPs TO THE "BGP CONFIG,ROUTE FILTERS CONFIG" 
        '''
        print "ASSIGN THE GENERATED IPs to BGP CONFIG,ROUTE FILTERS CONFIG"
        for key,values in hosts_dict.iteritems():
            hostname = key
            filter_list = list()
            for key,vals in values.iteritems():
	        if key == "bgp":
	            for val in vals:
		        bgp_remote_host = val["remote_description"]
		        for link in links:
		            if hostname == link["local_system"] and bgp_remote_host == link["remote_system"]:
            	    	        val["remote_peer"] = link["remote_ip"].replace("/30","")
			        filter_list.append(val["remote_peer"]+"/32")
		            elif hostname == link["remote_system"] and bgp_remote_host == link["local_system"]:
	    		        val["remote_peer"] = link["local_ip"].replace("/30","")
			        filter_list.append(val["remote_peer"]+"/32")
            for filter in filter_list:
                values['route_filter'].append(filter)

        '''
        ASSIGN THE GENERATED IPs TO THE "BGP CONFIG,ROUTE FILTERS CONFIG"
        '''
        print "ASSIGN THE GENERATED IPs to BGP CONFIG,ROUTE FILTERS CONFIG"
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

        '''
        CONFIG TEMPLATE
        '''
        template_filename = "QFX_eBGP.conf"
        complete_path = os.path.join(os.getcwd(), 'Config')
        template_file = complete_path + "/" + template_filename

        for spine_ip in spine_ips:
            helpers.load_template_config(spine_ip,hosts_dict,template_file)

        '''
        CONFIG TEMPLATE
        '''
        template_filename = "QFX_iBGP.conf"
        complete_path = os.path.join(os.getcwd(), 'Config')
        template_file = complete_path + "/" + template_filename

        for spine_ip in spine_ips:
            helpers.load_template_config(spine_ip,hosts_dict,template_file)

        '''
        CONFIG TEMPLATE
        '''
        template_filename = "QFX_vlans.conf"
        complete_path = os.path.join(os.getcwd(), 'Config')
        template_file = complete_path + "/" + template_filename

        for spine_ip in spine_ips:
            helpers.load_template_config(spine_ip,hosts_dict,template_file)

        '''
        CONFIG TEMPLATE
        '''
        template_filename = "QFX_routing_instance.conf"
        complete_path = os.path.join(os.getcwd(), 'Config')
        template_file = complete_path + "/" + template_filename

        for spine_ip in spine_ips:
            helpers.load_template_config(spine_ip,hosts_dict,template_file)

        '''
        CONFIG TEMPLATE
        '''
        template_filename = "QFX_ae.conf"
        complete_path = os.path.join(os.getcwd(), 'Config')
        template_file = complete_path + "/" + template_filename

        for spine_ip in spine_ips:
            helpers.load_template_config(spine_ip,hosts_dict,template_file)
