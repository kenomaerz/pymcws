import pymcws as mcws
import time
from datetime import timedelta

# Create the server using access key and credentials
# Dont forget to replace the example key with one that you can reach
# the server is resolved laizily, i.e. once the first command is sent
office = mcws.get_media_server("AccessKey", "readonly", "supersecretpassword")

# Alternatively, just use the keyword 'localhost', this avoids the delay.
# You can also set info manually.
office = mcws.get_media_server("localhost", "readonly", "supersecretpassword")


# Query files via query recipe
files = mcws.query_album(office, "Ludovico Einaudi", "I Giorni")
# files are dictionaries of tags. Tags are automatically converted to the correct python type.
print(files[0]["Date"])
print(files[0]["Name"])
print(files[0]["Duration"])

# Editing tags is easy! Just edit the dict, and save the file afterwards
# Files keep track of the changes that are made and only send relevant data
# to the server. All data is escaped and converted automatically.
files[0]["Name"] = "Test2,3,4"
files[0]["Genre"] = ["Test Genre 3,7", "Test Genre 3,5", "Test Genre 6"]
files[0]["Date"] += timedelta(years=10)
files[0]["Rating"] = 4
# You can check which fields have been changed
print(files[0].changed_fields)
# Finally, tell the server to persist the changes
# next lines are commented out for safety
# mcws.file_set_info(office, files[0])
# If you don't want to persist all changes, filter the fields you want to edit:
# mcws.file_set_info(office, files[0], {"Name", "Rating"})

# Play an album using a play recipe. Replace this with one that you have
print("Playing an Album")
mcws.play_album(office, "Ludovico Einaudi", "I Giorni", repeat=False)
time.sleep(3)
print("Pausing playback")
mcws.playback_playpause(office)

# Find and print the available Zones on the server
zones = mcws.playback_zones(office)
print("Zones available at server:")
for zone in zones:
    print("    ", zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)

# files_search lets you execute arbitrary queries and playback (optionally using zones)
mcws.files_search(office, query="[Artist]=[Sting]", action="Play", zone=zones[0])
time.sleep(3)

# all playback commands can be used with a zone, same as the mcws API.
# Lets blindly play/pause the first returned zone
print("Play/Pausing first returned zone")
mcws.playback_playpause(office, zones[0])

# move the play postion forward by thirty seconds and play/pause again
print("Jumping to position (ms): " + str(mcws.playback_position(office, 30000)))
mcws.playback_playpause(office, zones[0])

# Adjust volume
print("Setting volume to 0, increasing it by .1 five times")
# Set absolute volume
mcws.playback_volume(office, 0)
# set relative volume
for i in range(0, 5):
    print("    + 10%: " + str(mcws.playback_volume(office, 0.1, relative=True)))
    time.sleep(0.4)

# Muting
print("Mute state is: " + str(mcws.playback_mute(office)))
print("    Muting, new state: " + str(mcws.playback_mute(office, True)))
time.sleep(1)
print("    Unmuting, new state: " + str(mcws.playback_mute(office, False)))

# Repeat
print("Repeat mode is: " + mcws.playback_repeat(office))
print(
    "    Turning playlist repeat on, new state: "
    + mcws.playback_repeat(office, "Playlist")
)
print("    Turning repeat off, new state: " + mcws.playback_shuffle(office, "Off"))


# Shuffling
print("Shuffle mode is: " + mcws.playback_shuffle(office))
print("    Turning shuffle on, new state: " + mcws.playback_shuffle(office, "On"))
print("    Reshuffling playlist: " + mcws.playback_shuffle(office, "Reshuffle"))
mcws.playback_stop(office)

# Loading a DSP Preset
print("Loading DSP preset 'EQ Flat', probably not present on your box")
mcws.playback_loadDSPreset(office, "EQ Flat")
