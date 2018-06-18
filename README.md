# Sonos Reboot Utility
Have you ever wanted to reboot all of your Sonos devices without walking from room to room, that's exactly what this code does. 

## Reboot Order
In order to reboot successfully we make an attempt to enumerate the network interfaces recognized by Sonos's spanning tree, and use that to build the order in which devices reboot to ensure the traffic gets through to all of the zones. The order we choose to reboot the zones is as follows:
1. Sonos zones that are connected only by ethernet 
  * This typically is seen when you have a Play:Amp wired directly to a Playbar in a 5.1 setup, or you have manually disabled the WiFi interface on a zone.
2. Sonos zones that are connect wirelessly only
3. Sonos zones that are connected both wirelessly and by ethernet

