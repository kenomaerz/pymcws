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
pipenv install pymcws
```

First order of action is to import pymcws. You can just import the package and use
it as a one-stop-shop-all:

```python
import pymcws as mcws
```

using this method, all functions and recipes are imported and available via the
mcws object. You can then initialize a server and start using commands:

```python
office = mcws.get_media_server("AccessKey", "readonly", "supersecretpassword")
mcws.play_album(office, "Ludovico Einaudi", "I Giorni")
mcws.playback_playpause(office)
zones = mcws.playback_zones(office)
for zone in zones:
    print(zone.index, zone.id, zone.name, zone.guid, zone.is_dlna)
mcws.playback_playpause(office, zones[0])

```

For a full set of examples, please see examples.py.

## Contributing
Contributions are very welcome. Please create pull requests at your leisure.
If you are not of the coding kind, you can also leave a request for a specific
functionality in the issue tracker.  
