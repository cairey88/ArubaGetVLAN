#import modules
import netmiko
import sys
import re
import time
from netmiko import ConnectHandler
from getpass import getpass

#Prompt user for device input
ipaddress = input("Enter switch IP: ")
username = input("Enter switch username: ")
password = getpass()

#Start Timer
count = 0
start = time.time()

#Connect to each device
net_connect = ConnectHandler(device_type='hp_procurve', ip=ipaddress, username=username, password=password, global_delay_factor=2)

#find prompt and remove hash, save as name variable
name = net_connect.find_prompt() [:-1]

#declare variables
carriagereturn = " "
command = "sh int"

#send commannds to switch
net_connect.send_command(carriagereturn)
results = net_connect.send_command(command)

#Split result into list
lines = results.splitlines()

#function to find numbers
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

#create empty list
portlist = []

#If line contains a number take the first number of each line and add to port list.
for line in lines:
    if hasNumbers(line):
        fields = line.strip().split()
        portlist.append(fields[0])

#filename = name of switch + csv
filename = name+".csv"

#Open file
f = open(filename,'w')

#Write headers
f.write("Port,VLANS \n")

#for each line in list
for port in portlist:

        #write port number
        f.write(port+",")

        #Check for trunks, if Trk in port split on - and take trailing text
        if "Trk" in port:
            port = port.split("-")[1]

            #send command
            commandvlan="sh vlans ports "+port+" detail"

            #Ssve result
            result = net_connect.send_command(commandvlan)

            #Print to screen
            print("port "+port+ " complete")

            #Split result into list, if tagged in result write VLAN to file
            for line in result.splitlines():
                if "Tagged" in line:
                    fields = line.strip().split()
                    f.write(fields[0]+",")
                
                #If untagged in list print VLAN and Untagged to file
                elif "Untagged" in line:
                    fields = line.strip().split()
                    f.write(fields[0]+" Untagged,")

        #Do the same as above for none trunk ports
        else:

            commandvlan="sh vlans ports "+port+" detail"

            result = net_connect.send_command(commandvlan)

            print("port "+port+ " analysed")

            for line in result.splitlines():
                if "Tagged" in line:
                    fields = line.strip().split()
                    f.write(fields[0]+",")
                

                elif "Untagged" in line:
                    fields = line.strip().split()
                    f.write(fields[0]+" Untagged,")

        f.write("\n")

        #Add to count each time ran
        count +=1

#Close connection to switch
net_connect.disconnect()

#Closef ile
f.close()

#End timer
end = time.time()        

#Print time
time = (end - start)
timeint = int(time)

print("COMPLETED " + str(count) + " ports analysed in " + str(timeint) + " seconds")

