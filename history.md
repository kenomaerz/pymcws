# Version History

### v1.0.0
* Major rewrite of pymcws that fixes everything I started to dislike about the structure.
* Usage is more intuitive now, see Readme.md and example.py for details.
* Editing and saving files is now possible.
* Several additional endpoints implemented.
* Finally added tests.

### v0.2.2
* Implemented playback_loadDSPPreset based on https://github.com/kenomaerz/pymcws/issues/6.

### v0.2.1
* Introduced session management for established media servers.

### v0.2.0
* Added automatic field resolution. Fields are automatically converted to and from their corresponding python types by the API, sparing you the postprocessing.
* Because of this, the required version of MC is now 26. Earlier version support is possible but needs to be requested.
* Play recipes use more reasonable defaults for shuffle and repeat.
* Several smaller bugfixes.


### v0.1.0
* Added remote connection capabilities. The MediaServer class queries JRiver's web service and tries to determine the best possible connection method automatically.

### v0.0.7
* Fixed zones being ignored in play_recipes.

### v0.0.6
* Fixed failing package installation on case-aware file systems.

### v0.0.5
* Created query recipes for easier querying.
* Improved image and cover art handling.
* Implemented library_values.
* Implemented automatic query escaping for the jriver search language.
* Play recipes allow  setting shuffle and repeat states.
* Introduced zone handling.
* Full automatic local ip resolution, also for multiple network adapters.

### v0.0.4
* Support for getting file info and parsing MPLs.
* Support for getting images for library files.
* More lenient timeouts for local connections should prevent huge queries from failing.

### v0.0.3
* MediaServer now throws exception if key cannot be resolved instead of failing silently.
* Added mute, shuffle and repeat.
* Added volume control.
* Improved example.py to explain usage better.
* Fixed wrong behavior of playback_stop.

### v0.0.2
* api.py now has a method to get a server directly from pymcws object. This allows basic usage by only importing pymcws.

### v0.0.1
* Initial release and proof of concept.
* Resolve media network access keys.
* Issue playback commands.
* Search and play files to different zones on server.
* First play_recipes that facilitate playback of files.
