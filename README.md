HypeMergence
======================

###Final project for Zipfian Academy: predicting emerging artists from HypeM's Latest Blogged Artists
--------------------------------------

HypeMergence is a web app that displays a rank of how emerging artists, collected from [Hypem's Latest Blogged](http://hypem.com/latest/noremix), will be. Their rank is derived from a support vector machine classification on data from [Echonest](http://the.echonest.com/) and [Next Big Sound(NBS)](https://www.nextbigsound.com/).

Artists are ranked, from left to right, according to their probablity of being an emerging artist. Emerging artists are labeled in yellow, whereas artists in white are unfortunately not so much. 

**Check it out here: [HypeMergence](http://bit.ly/1nYCk7q)(Chrome and Safari only)**

*For some goodies, if you click the artist you'll get their song via SoundCloud. If you hover, you'll see the change in traction of their social media account over time - normalized to account for artists with less overall followers/listens/etc.*

<img src="https://raw.githubusercontent.com/dubtran/hypemergence/master/imgs/Screen%20Shot%202014-07-29%20at%2011.48.26%20PM.png">
--------------------------------------
####Here's what you'll see in this github repo

#####Featurization

- **blogged_collection.py**: Creates an object with the following instances: 
	- Artists: list of recently blogged about artists from HypeM
	- Features: Echonest parameters, and linear regression parameters(coefficient and intercept) of timeseries data
	- Results: Predicted classification, and probability of classification 
	- URLs of images for webapp collected from Echonest.
	- URLs of SoundCloud tracks for webapp from SoundCloud
- **nbs_ft.py**: Collection of NBS timeseries data over all social media platforms, including SoundCloud, YouTube, Facebook, etc. Functions parse data and convert their unix datetime to readable datetime. 

#####Webapp

- **hypemer_app.py**: Flask app
- **store_blogd.py**: Main module called to cache results created by blogged_collection for webapp access. 
- **start.html**: Main html for webapp
- **sweetsvm.pkl**: Main SVM model used predict if artist is emerging or not

####Required modules
* [NextBigSoundAPI python handler](https://github.com/buckheroux/NBS-API-Python)
* [Pyen - Echonest python handler](https://github.com/echonest/pyen)
* [Soundcloud - python handler](https://github.com/soundcloud/soundcloud-python)
* [Flask app](http://flask.pocoo.org/)
* [Rickshaw](https://github.com/shutterstock/rickshaw)
* [D3](https://d3js.org/)

###### *The process of exploring data and choosing which model to use can be seen in the folder theroadtohypemergence* 


----------------

##HypeMergence's purpose and details

HypeMergence is a result of my capstone project for [Zipfian Academy](http://www.zipfianacademy.com/), with the residual benefits of allowing users to see, of those recently blogged (collected on Hypem), who would be worth their time and efforts - or *emerging*. As there are many various attributes to consider when determining if an artist is 'emerging', I have decided to attempt to detect emergence via Social Media metrics. 

Artists' social media metrics were featurized by running a linear regression through a normalized difference over time. The regression returned a coefficient, describing the over all trend over time, and an intercept, repesenting the mean change over time. The metrics spanned over 90 days and include:

- <u>Facebook</u>: likes and fans
- <u>SoundCloud</u>: plays, fans, and comments
- <u>Twitter</u>: mentions, retweets, statuses, friends, and fans
- <u>YouTube</u>: fans, likes, and plays
- <u>Last.fm</u>: fans, comments, and plays
- <u>Instagram</u>: comments, fans, and friends 
- <u>Rdio</u>: collections, playlists, and plays
	 
Alongside these metrics, I have also included Echonest's parameters:

- hotttnesss: This corresponds to how much buzz the artist is getting right now. This is derived from many sources, including mentions on the web, mentions in music blogs, music reviews, play counts, etc.
- discovery: This is a measure of how unexpectedly popular the artist is.
- familiarity: How well known in artist is. You can look at familiarity as the likelihood that any person selected at random will have heard of the artist.
- Total blog mentions to song ratio 

For validation, I attempted to classify [Billboard's Emerging Artists](http://realtime.billboard.com/?chart=emergingartists). *My app differs from this, because Billboard has a limited list of artists (140) and only takes the top trending tweeted about song/artist within the last 24 hours. Whereas my app, takes an artist that is blogged and tells you if he/she/they  could be on Billboard's*

My linear support vector classifier - from [SKLearn](http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) - got an accuracy of 94.73%, precision of 98.39%, and recall of 85.91%. <- As a note a lower recall is a problem, because falsely emerging artists can lead to a waste of time or investment. 

With that, if you're interested in getting more insight to the two weeks of my struggles and pains in creating this app, please visit [my blog](http://www.medium.com/@dubtran)

###Thanks for getting this far and your interest in HypeMergence :D 
