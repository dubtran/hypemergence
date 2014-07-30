import soundcloud as sc
import pyechonest as pyecho
import pyen
import requests 
import bs4
import json
import urllib
from semetric.apiclient import SemetricAPI
from semetric.apiclient.entity import Artist
import psycopg2 as psyco 
import retreive_NBS_data

#get id for Soundcloud using artists' url 
def get_id(urls, client):
	return client.get('/resolve', url = urls).id

#Getting timestamps of soundcloud comments on each of the tracks -- might not need this
def get_comments(tracks):
	comments = dict()
	for t in tracks:
		comments[t]= [c.timestamp for c in client.get('/tracks/%d/comments' % t)]
	return comments

'''
Getting list of artists - ROWS - from hypem.
Here used latest blog posts of noremixes. 
@param: total : *20 for total artists' names
@returns: a set of artists collected from hypem's noremix latests
'''
def getArtists(total):
	artists = []
	for t in xrange(total):
		data = requests.get('http://hypem.com/playlist/latest/noremix/json/%d/data.js' %t)
		if data.status_code == 200: 
			data = data.json()
			for d in data.keys():
				if d != 'verison' and d == int:
					artists.append(data[d]['artist'])
		else:
			sleep(10s)
	return artists

'''
Creates a dict of echonest params [hotttness, discovery, familiarity]
@param: list of artists
@return: dataframe
'''
def getEcho_df(artists):
	emerge_data = []
	for a in artists:
	    try:
	        emerge_data.append(eco.get('artist/profile', name = str(a), bucket = ['hotttnesss' , 'discovery', 'familiarity']))
	    except Exception , e: 
	        print 'cant get ', a 
	        
	discover = []
	hotness = []
	familiar = []
	art_p = []

	for x in emerge_data:
	    discover.append(x['artist']['discovery'])
	    hotness.append(x['artist']['hotttnesss'])
	    familiar.append(x['artist']['familiarity'])
	    art_p.append(str(x['artist']['name']))
	temp_pdf = pd.DataFrame(zip(art_p, hotness, discover, familiar))
	temp_pdf.columns = ['artist', 'hottness', 'discovery', 'familiarity']
	temp_pdf = temp_pdf.set_index('artist')

	return temp_pdf

'''
Getting timeseries data from semetric
@param: list of which time series (plays, comments, page views)
@param: artist connected to sem api 
@return: dataframe of timeseries data
'''
def getTimeSeries(artist, params):
    timeseries= params
    timedf = pd.DataFrame()
    for i, ts in enumerate(timeseries): 
        try: 
            time = artist.timeseries(ts)
            newtime = []
            for t, value in time:
                dt = datetime.utcfromtimestamp(t)
                timestamp = dt.strftime("%Y-%m-%d")
                newtime.append((timestamp,value))
            newtime = pd.DataFrame(newtime)
            newtime.columns = ['date', ts]
            newtime = newtime.set_index('date')
            
            if len(timeseries) > 1 :
                timedf = timedf.join(newtime, how = 'outer')
            else: 
                timedf = newtime
        except Exception, e:
            print "errors ", e[0]
            print 'not working on : ', ts
        timedf['artist'] = artist.name
    return timedf

'''
Collecting list of billboard emerging artists using kimono labs
- here emerging is defined as up-and-coming artists on twitter with most shared songs 
@params none
@return list of artists' name, dict of artist and values(%change in position, %change in stats) 
'''
def getBillboard(): 
	emerging = json.load(urllib.urlopen("https://www.kimonolabs.com/api/d13oeuo6?apikey=b84997b282ae1ebcbaca9da9ce786cb9"))
	em_names = []
	em_values = dict()
	for x in emerging['results']['collection1']:
	    breakoff = x['artist']['text'].find('{')
	    name = x['artist']['text'].encode('ascii')[:breakoff]
	    em_names.append(name)
	    em_values[name] = x['artist']['text'][breakoff:]

	return em_names, em_values

''' 
Storing values into SQL database
@param: query, values
'''
def storeSQL(query, values, many = False):
	cur = conn.cursor()
	if many == False: 
		cur.execute(query, values)
	else:
		cur.executemany(query, values)
	conn.commit()
	return '...stored...'

#determining if an artist is emerging or not
def ifEmerge(): 
	pass

def main():
	

	#getting and storing emerging artists
	# emer_query = "insert into billboard_emerge(name) values (%s)"
	# em_art, em_val = getBillboard()
	# for art in em_art:
	# 	storeSQL(emer_query, (art,))

	#getting hypem artists/checking echonest value

	conn.close()
	#to create time series then store it
	ts_dfs = []
	for i, a in enumerate(artists):
	    try:
	        art = api.search(Artist, name = a[0])
	        art = api.get(Artist, id=art[0].id)
	        ts_Df = getTimeSeries(art)
	        ts_dfs.append(ts_Df)
	    except Exception, e:
	        print i, a, 'has a problem' 
	        print 'error: ', e[0]

if __name__ == '__main__':
	conn = psyco.connect(dbname = 'nebulae')
	#Set up Soundcloud wrapper
	sc_id = '6deaad13ebe3e5d68a5c54c36df9d397'
	secret = '0cefa60dc4b5ab9782e2d1cced0d7867'
	client = sc.Client(client_id = sc_id, client_secret = secret)

	#Echonest wrapper
	eco_api = "NCBSJDMBE39OEZKBZ"
	eco = pyen.Pyen(eco_api)

	#Semetric api wrapper
	sm_id= "8db8b6311dc44f6ea32b0331f9cf8b5f"
	sem_api = SemetricAPI(sm_id)
	main()


