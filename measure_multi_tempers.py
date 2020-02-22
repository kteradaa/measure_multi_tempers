#!/usr/bin/python3

import subprocess
import sys
import datetime
import os

cmd_tempered_path = '/usr/local/bin/tempered'
cmd_hidquery_path = '/usr/local/bin/hid-query'

# --- Get HIDRAW devices as list

cmd = "ls -1 /dev/hidraw*"
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

# sys.stdout.buffer.write( res.stdout )

device_list = res.stdout.decode("utf8").splitlines() 
# print( res.stdout.decode("utf8").splitlines() )

devname = []
vidpid = []
physical = []

for item in device_list:
	#print("HIDRAW device found : "+item)

	cmd = cmd_hidquery_path + " -p " + item
	res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

	str = res.stdout.decode("utf8")	

	query_list = res.stdout.decode("utf8").split(' ')
	
	#print( "DeviceID:ProductID = " + query_list[3].rstrip() )
	#print( "Physical Address = " + query_list[8].rstrip() )

	devname.append( item )
	vidpid.append( query_list[3].rstrip() )
	physical.append( query_list[8].rstrip() )

#for dev, id, phys in zip( devname, vidpid, physical ):
	#print( "dev = " + dev + " id = " + id + " phys = " + phys )

# --- Read devlist file

path = os.path.dirname(__file__) + '/devlist'
devlist_phys = []
with open(path) as fp:
	bufs = fp.readlines()
	for str in bufs:
		devlist_list = str.split(' ')
		devlist_phys.append( devlist_list[8].rstrip() )

#for phys in devlist_phys:
	#print( "devlist phys = " + phys )

# --- Looking out HID device name for each phys in devlist 

meas_number = 1
for phys in devlist_phys:
	if phys in physical :	
		match_idx = physical.index( phys )

		#print( "phys " , phys , " matched to index " , match_idx , " as " , physical[match_idx] )
		#print( "phys " + phys + " device = " + devname[match_idx] + " vid/pid = " + vidpid[match_idx] )

		if vidpid[match_idx] == '413d:2107' :
		
			cmd = cmd_tempered_path + " " + devname[match_idx] 
			res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			#print( res.stdout.decode("utf8").rstrip() )
		
			meas_list = res.stdout.decode("utf8").splitlines() 
			temperature = 'no measure'
			for str in meas_list:
				bufs = str.split(' ')
				#print( bufs )
				if bufs[2] == "temperature" :
					temperature = bufs[3]
			
			now = datetime.datetime.now()
			str_datetime = '{0:%Y-%m-%d %H:%M:%S}'.format(now)
			print( meas_number, str_datetime, phys + " " + temperature )
			#meas_number += 1
	else :
		print( "Error: Device " + phys + " that specified in " + path + " is not found on USB-bus anymore." )
	
	meas_number += 1

# end of code

