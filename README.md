HypeMergence
======================

###Final project for Zipfian Academy: predicting emerging artists from HypeM's Latest Blogged Artists
--------------------------------------
~ An attempt to check out *emerging* musicians that are currently being blogged about

HypeMergence is a web app that collects artists from [Hypem's Latest Blogged](http://hypem.com/latest/noremix) and their data from [Echonest](http://the.echonest.com/) and [Next Big Sound(NBS)](https://www.nextbigsound.com/). It then runs some "magic" or rather *analytics* on the data collected to then show you if the artist will be emerging or not. 

Artists are ranked, from left to right, according to their probablity of being an emerging artist

Emerging artists are labeled in yellow, whereas artists in white are unfortunately not so much. 

**Check it out here: [HypeMergence](http://bit.ly/1nYCk7q)**

--------------------------------------
####Here's what you'll see
#####Featurization

- **blogged_collection.py**: Creates an object with the following instances: 
	- Artists: list of recently blogged about artists from HypeM
	- Features: Echonest parameters, and linear regression parameters(coefficient and intercept) of timeseries data
	- Results: Predicted classification, and probability of classification 
	- URLs of images for webapp collected from Echonest.
	- URLs of Soundcloud tracks for webapp from SoundCloud
- **nbs_ft.py**: Collection of NBS timeseries data over all social media platforms, including SoundCloud, YouTube, Facebook, etc. Functions parse data and convert their unix datetime to readable datetime. 

#####Webapp

- **hypemer_app.py**: Flask app
- **store_blogd.py**: Main module called to cache results created by blogged_collection for webapp access. 
- **start.html**: Main html for webapp

####Required modules
=======
* [Flask app](http://flask.pocoo.org/)
* [NextBigSoundAPI python handler](https://github.com/buckheroux/NBS-API-Python)
* [Pyen - Echonest python handler](https://github.com/echonest/pyen)
* [Soundcloud - python handler](https://github.com/soundcloud/soundcloud-python)
