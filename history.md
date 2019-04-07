# Version History
### v0.0.4
* Support for getting file info and parsing MPLs
* Support for getting images for library files
* More lenient timeouts for local connections should prevent huge queries from failing

### v0.0.3
* MediaServer now throws exception if key cannot be resolved instead of failing silently
* Added mute, shuffle and repeat
* Added volume control
* Improved example.py to explain usage better
* Fixed wrong behavior of playback_stop

### v0.0.2
* api.py now has a method to get a server directly from pymcws object. This allows basic usage by only importing pymcws.   

### v0.0.1
* Initial release and proof of concept
* Resolve media network access keys
* issue playback commands
* search and play files to different zones on server
* first play_recipes that facilitate playback of files  
