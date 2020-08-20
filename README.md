# pyMCWS
A python API wrapper for MCWS, the web interface of the excellent JRiver Media Center.
The aim is to replicate the MCWS functionality as close as possible in a pythonian,
easy to use manner. Additionally, common use-cases can be implemented in
easily accessible recipes.

Currently, the minimum required version of JRiver MC is 26. Backwards compatibility is possible,
but will have to be requested - it is mainly the automatic field conversion that is preventing it.

## Usage
use your package manager of choice to install pymcws:

```bash
pip install pymcws
```

First order of action is to import pymcws. You can just import the package and use
it as a one-stop-shop-all:

```python
import pymcws as mcws
```

using this method, all functions and recipes are imported and available via the
mcws object. You can then initialize a server and start using commands:

```python
# get the server
office = mcws.get_media_server("AccessKey", "readonly", "supersecretpassword")
# use a recipe to play an album
files = office.recipes.query_album("Ludovico Einaudi", "I Giorni")
office.playback.playpause()
zones = office.playback.zones()
for zone in zones:
    print(zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)
office.playback.playpause(zones[0])

```

For a full set of examples, please see examples.py.

## Using the API and recipes
pymcws wraps the MCWS API in a 1:1 manner. If you are looking for http://localhost:52199/MCWS/v1/Playback/Stop,
then that's located under pymcws.playback.stop. This way, you can import API functions to your scripts as needed.

To call these functions, you need a server. The easiest way to get one is to call pymcws.get_media_server() along with an access key, username and password. The server returned in this way already imports the API functions and provides them locally. These two calls are functionally identical:

```python
# get the server
office.playback.playpause()
mcws.playback.playpause(office)
```

Use whichever you prefer. If you intend to use the second option exclusively, consider using pymcws.get_media_server_light() to get your server - the returned class does not import API functions directly.

The general philosophy of pymcws is to make communication with mcws as easy as possible. Wherever possible, 
the behaviour if the API has been replicated 1:1, where exceptions exist, they are documented. The main difference is that pymcws provides classes that model complex entities like zones and files, and uses these
classes to facilitate interaction. More on these classes in the following sections.

Finally, pymcws provides convenience methods that enable users to quickly execute common tasks. These are 
stored in pymcws.recipes and contain functionality like playing and querying albums.

## The MediaServer class
The MediaServer class covers all functionality to communicate with JRiver Media Center.
The most important feature is connection negotiation. When providing an access key, the server is resolved,
and the best connection strategy is chosen. Inside your home network, this will be the local IP,
outside it will be global IP.

## Working with Files
JRiver Media Center has a complex model for files and allows adding custom fields with varying types.
pymcws queries these field definitions and automatically performs type conversions for them, allowing users 
to work with common types like string, int, float, datetime etc. directly. These conversions happen both ways:
When saving changes to files, the types are converted back to jriver-compatible versions. 

Files themselves are simply (extended) dictionaries. Calling my_file["Date"] returns the datetime of the corresponding field. Changing values works the same way as well, but changes are not persisted immediately. Files keep track of which values you have modified. Once you are happy, call pymcws.file.set_info() and pass it the file to save the changes. pymcws will only transmit changed and new fields.
Please do not create a file yourself, as jriver takes care of assigning a key. Instead,
call pymcws.library.create_file to get a new file and start populating it with values.

## Working with Zones
Zones are the places where you can play music, accordingly they are mainly used for playback commands.
List them with pymcws.playback.zones(), and use them to specify which zone the command is for.
The zone argument is always optional, if no zone is provided, JRiver Media Center will use the zone currently selected in the UI.

## The function I need is not in pymcws!
That's quite possible. I mainly extend pymcws as I need new features. The current structure makes it easy to add
functionality quickly. Please feel free to open an issue in the issue tracker.

## Contributing
Contributions are very welcome. Please create pull requests at your leisure.
If you are not of the coding kind, you can also leave a request for a specific
functionality in the issue tracker.  
