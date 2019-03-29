import pymcws as mcws
from pymcws import MediaServer
import time

# Create the server using access key and credentials
# Dont forget to replace the example key with one that you can reach
office = MediaServer("SdYoPV", "readonly", "supersecretpassword")

# Play an album using a play recipie
mcws.play_album(office, "Ludovico Einaudi", "I Giorni")
time.sleep(3)
mcws.playback_playpause(office)

# Play a keyword using play recipies. Do you have keyowrds assigned to your music files?
mcws.play_keyword(office, "Lounge", shuffle=False)
time.sleep(3)

# Find and print the available Zones on the server
zones = mcws.playback_zones(office)
for zone in zones:
    print(zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)

# all playback commands can be used with a zone, same as the mcws API.
# Lets blindly play/pause the first returned zone
mcws.playback_playpause(office, zones[0])

# move the play postion forward by thirty seconds and play/pause again
print(mcws.playback_position(office, 30000))
mcws.playback_playpause(office, zones[0])
