import sys
import re
import requests.sessions as RequestsSessions
import requests.adapters as RequestsAdapters
import xml.etree.ElementTree as ElementTree

#from requests.adapters import HTTPAdapter

# Function to initiate the reboot of a zone.
def rebootzone(ipAddress):
    session = RequestsSessions.session()
    session.keep_alive = False
    session.mount('http://', RequestsAdapters.HTTPAdapter(max_retries=5))
    rebooturl = "http://" + ipAddress + ":1400/reboot"
    rebootget = session.get(rebooturl, timeout=5)
    rebootresponse = ElementTree.fromstring(rebootget.text)
    for body in rebootresponse:
        csrftoken =  body.find('form').find('input').attrib["value"]
        session.post(rebooturl, { "csrfToken" : csrftoken }, timeout=5)
    return

# Access a zone and uses its support page to enumerate all zones
def enumeratezones(ipaddress):
    zoneurl = "http://" + ipaddress + ":1400/support/review"
    session = RequestsSessions.session()
    session.keep_alive = False
    session.mount('http://', RequestsAdapters.HTTPAdapter(max_retries=5))
    zoneget = session.get(zoneurl, timeout=5)
    zones = list()

    # Build and traverse XML tree for support page
    zpnetworkinfo = ElementTree.fromstring(zoneget.content)
    for zpsupportinfo in zpnetworkinfo.iter('ZPSupportInfo'):
        zpinfo = zpsupportinfo.find('ZPInfo')
        zonename = zpinfo.find('ZoneName').text
        ipaddress =  zpinfo.find('IPAddress').text
        ethernetcount = 0
        wirelesscount = 0

    #Get spanning tree information to determine the order to reboot devices.
        commands = zpsupportinfo.iter("Command")
        for command in commands:
            if command.attrib["cmdline"].startswith('/usr/sbin/brctl showstp'):
                # Count active ethernet interfaces
                pattern = re.compile(r'eth\d.*?state.*?$', re.DOTALL | re.MULTILINE)
                matches = pattern.finditer(command.text)
                if matches is not None: 
                    for match in matches:
                        result = match.group()
                        pattern = re.compile(r'forwarding', re.DOTALL)
                        match = pattern.search(result)
                        if match is not None: ethernetcount += 1
                # Count active wireless interfaces
                pattern = re.compile(r'ath\d.*?state.*?$', re.DOTALL | re.MULTILINE)
                matches = pattern.finditer(command.text)
                if matches is not None: 
                    for match in matches:
                        result = match.group()
                        pattern = re.compile(r'forwarding', re.DOTALL)
                        match = pattern.search(result)
                        if match is not None: wirelesscount += 1
        rebootorder = 0
        if wirelesscount == 0:
            rebootorder = 0
        else:
            rebootorder = 1000*ethernetcount+wirelesscount
        zone = [zonename, ipaddress, rebootorder]
        zones.append(zone)
        zones = sorted(zones,key=lambda weight:weight[2])
    return zones

print "Rebooting zones:"
for zone in enumeratezones(sys.argv[1]):
    print("\t" + zone[0] + " (IP: " + zone[1] + "   Weight: " + str(zone[2]) + ")")
    rebootzone(zone[1])



