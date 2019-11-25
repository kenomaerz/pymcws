# Version History
### v0.0.5
* Created query recipes for easier querying
* Improved image and cover art handling
* Implemented library_values
* Implemented automatic query escaping for the jriver search language
* Play recipes allow  setting shuffle and repeat states
* Introduced zone handling 
* Full automatic local ip resolution, also for multiple network adapters

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
* Issue playback commands
* Search and play files to different zones on server
* First play_recipes that facilitate playback of files  
