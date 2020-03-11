#!/usr/bin/python3

import subprocess
import sys
import datetime
import os

cmd_tempered_path = '/usr/local/bin/tempered'
cmd_hidquery_path = '/usr/local/bin/hid-query'

# --- Check options

args = sys.argv
if( len(args) == 2 and args[1] == '-v' ) : # verbose mode
	verbose = True
else:
	verbose = False

if( len(args) == 3 and args[1] == '-o' ) : # output to specified file instead of stdout
	output_file = args[2]
else:
	output_file = ''


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

output_buf = ""
now = datetime.datetime.now()
str_datetime = '{0:%Y-%m-%d %H:%M:%S}'.format(now)
if( not verbose ) :
	output_buf = output_buf + str_datetime

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
			if( verbose ) :
				output_buf = output_buf + '{0:03d}'.format(meas_number) + " " + str_datetime + " " + phys + " " + temperature
				print( output_buf )
				output_buf = ""
			else :
				output_buf = output_buf + ", " + temperature
	else :
		print( "Error: Can not found device " + phys + " that specified in " + path + " on USB-bus anymore." ,file=sys.stderr )
	
	meas_number += 1

if( not verbose ) :
	if( output_file == "" ) :
		print( output_buf )
	else :
		fp = open( output_file, "w" )
		print( output_buf, file=fp )
		fp.close()

# end of code

