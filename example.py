import pymcws as mcws
import time

# Create the server using access key and credentials
# Dont forget to replace the example key with one that you can reach
# the server is resolved laizily, i.e. once the first command is sent
office = mcws.get_media_server("AccessKey", "readonly", "supersecretpassword")

# Alternatively, just use the keyword 'localhost', this avoids the delay.
# You can also set info manually.
office = mcws.get_media_server("localhost", "readonly", "supersecretpassword")

# Play an album using a play recipe. replace this with one that you have
print("Playing an Album")
mcws.play_album(office, "Ludovico Einaudi", "I Giorni")
time.sleep(3)
print("Pausing playback")
mcws.playback_playpause(office)

# Find and print the available Zones on the server
zones = mcws.playback_zones(office)
print("Zones available at server:")
for zone in zones:
    print("    ", zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)

# all playback commands can be used with a zone, same as the mcws API.
# Lets blindly play/pause the first returned zone
print("Play/Pausing first returned zone")
mcws.playback_playpause(office, zones[0])

# move the play postion forward by thirty seconds and play/pause again
print("Jumping to position (ms): " + str(mcws.playback_position(office, 30000)))
mcws.playback_playpause(office, zones[0])

# Adjust volume
print("Setting volume to 0, the increasing by .1 five times")
mcws.playback_volume(office, 0)
for i in range(0, 5):
    print("    + 10%: " + str(mcws.playback_volume(office, 0.1, True)))
    time.sleep(0.4)

# Muting
print("Mute state is: " + str(mcws.playback_mute(office)))
print("    Muting, new state: " + str(mcws.playback_mute(office, True)))
time.sleep(1)
print("    Unmuting, new state: " + str(mcws.playback_mute(office, False)))

# Repeat
print("Repeat mode is: " + mcws.playback_repeat(office))
print("    turning playlist repeat on, new state: " + mcws.playback_repeat(office, 'Playlist'))
print("    Turnign repeat off, new state: " + mcws.playback_shuffle(office, 'Off'))


# Shuffling
print("Shuffle mode is: " + mcws.playback_shuffle(office))
print("    turning shuffle on, new state: " + mcws.playback_shuffle(office, 'On'))
print("    Reshuffling playlist: " + mcws.playback_shuffle(office, 'Reshuffle'))

mcws.playback_stop(office)
