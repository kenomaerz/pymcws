import pymcws as mcws
import time
from datetime import timedelta

# Create the server using access key and credentials
# Dont forget to replace the example access key with one of your's
# the server is resolved lazily, i.e. once the first command is sent
# office = mcws.get_media_server("AccessKey", "readonly", "supersecretpassword")

# Alternatively, just use the keyword 'localhost' if the instance runs on your machine,
# this avoids the delay of resolving the access key.
office = mcws.get_media_server("localhost", "readonly", "supersecretpassword")

# Recipes bundle commonly used tasks into simple methods
# Query files via query recipe
files = mcws.recipes.query_album(office, "Ludovico Einaudi", "I Giorni")
# files are dictionaries of tags. Tags are automatically converted to the correct python type.
# This conversion happens both ways transparently. Just use the python types, pymcws takes care of the rest
print(files[0]["Date"])
print(files[0]["Name"])
print(files[0]["Duration"])

# Editing tags is easy! Just edit the dict, and save the file afterwards
# Files keep track of the changes that are made and only send relevant data
# to the server. All data is escaped and converted automatically.
files[0]["Name"] = "Test2,3,4"
files[0]["Genre"] = ["Test Genre 3,7", "Test Genre 3,5", "Test Genre 6"]
files[0]["Date"] += timedelta(days=365)
files[0]["Rating"] = 4
# You can check which fields have been changed
print(files[0].changed_fields)
# Finally, tell the server to persist the changes
# next lines are commented out for safety
# office.file.set_info(files[0])
# If you don't want to persist all changes, filter the fields you want to edit:
# office.file.set_info(files[0], {"Name", "Rating"})

# You can use lists of files all over pymcws, e.g. to set a playlist
files.pop(0)
office.playback.set_playlist(files=files)
time.sleep(3)

# Recipes bundle commonly used tasks into simple methods
# Play an album using a play recipe
print("Playing an Album")
mcws.recipes.play_album(office, "Ludovico Einaudi", "I Giorni", repeat_album=False)
time.sleep(3)
print("Pausing playback")
office.playback.playpause()

# Find and print the available Zones on the server
zones = office.playback.zones()
print("Zones available at server:")
for zone in zones:
    print("    ", zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)

# print the playlist of the default zone
playlist = office.playback.playlist(fields=["Name", "Artist"])
print("Currently playing:")
for item in playlist:
    print("    ", item["Artist"], " - ", item["Name"])

# files_search lets you execute arbitrary queries and playback (optionally using zones)
files_sting = office.files.search(
    query="[Artist]=[Sting]", action="Play", zone=zones[0]
)
time.sleep(3)

# all playback commands can be used with a zone, same as the MCWS API.
# Lets blindly play/pause the first returned zone
print("Play/Pausing first returned zone")
office.playback.playpause(zones[0])

# move the play postion forward by thirty seconds and play/pause again
print("Jumping to position (ms): " + str(office.playback.position(30000)))
office.playback.playpause(zones[0])

# Adjust volume
print("Setting volume to 0, increasing it by .1 five times")
# Set absolute volume
office.playback.volume(0)
# set relative volume
for i in range(0, 5):
    print("    + 10%: " + str(office.playback.volume(0.1, relative=True)))
    time.sleep(0.4)

# Muting
print("Mute state is: " + str(office.playback.mute()))
print("    Muting, new state: " + str(office.playback.mute(True)))
time.sleep(1)
print("    Unmuting, new state: " + str(office.playback.mute(False)))

# Repeat
print("Repeat mode is: " + office.playback.repeat())
print(
    "    Turning playlist repeat on, new state: " + office.playback.repeat("Playlist")
)
print("    Turning repeat off, new state: " + office.playback.shuffle("Off"))


# Shuffling
print("Shuffle mode is: " + office.playback.shuffle())
print("    Turning shuffle on, new state: " + office.playback.shuffle("On"))
print("    Reshuffling playlist: " + office.playback.shuffle("Reshuffle"))
office.playback.stop()

# Loading a DSP Preset
print("Loading DSP preset 'EQ Flat', probably not present on your box")
office.playback.loadDSPreset("EQ Flat")
