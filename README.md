# pyMCWS
A python API wrapper for MCWS, the web interface of the excellent JRiver Media Center.
Th aim is to replicate the MCWS functionality as close as possible in a pythonian,
easy to us manner. Additionally, common use-cases can be implemented in
recipes.

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
