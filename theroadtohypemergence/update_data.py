from sqlalchemy import create_engine
import psycopg2 as psyco
import json
import pandas as pd
from sklearn import preprocessing
from NBSAPIPythonmaster import nbs_api as nbs
import json
from datetime import datetime

nbsAPI = nbs.API('winifredtran')

def getBillboard(): 
	emerging = json.load(urllib.urlopen("https://www.kimonolabs.com/api/d13oeuo6?apikey=b84997b282ae1ebcbaca9da9ce786cb9"))
	em_names = []
	em_values = dict()
	for x in emerging['results']['collection1']:
	    breakoff = x['artist']['text'].find('{')
	    name = x['artist']['text'].encode('ascii', errors = 'ignore')[:breakoff]
	    em_names.append(name)
	    em_values[name] = x['artist']['text'][breakoff:]

	return em_names, em_values

def get_json(artists):
    
    dump_artist = dict()
    
    for a in artists:
        search = nbsAPI.artistSearch(a.encode('ascii', errors='ignore'))
        search_json = json.loads(search)

        #finding the exact match if not, default to first search
        artist_ix = 0
        for i, x in enumerate(search_json.values()):
            try:
                if x['name'].encode('ascii', errors = 'ignore') == a.encode('ascii', errors = 'ignore'): 
                    artist_ix = i 
            #Error caused by ill formated names 
            except Exception,e :
                print 'error for ', a, ' ', e[0]
                pass

        key = search_json.keys()[artist_ix]
        temp = nbsAPI.metricsArtist(key, opt = ['2010-01-01','2014-07-12', 'all' ])
        temp_json = json.loads(temp)
        dump_artist[a.encode('ascii', errors = 'ignore').rstrip()] = temp_json
    
    return dump_artist

def convert_json(dump_new):
	converted_nbs = dict()
	for a in dump_new.keys():
	    dict_types = dict()
	    #unpacking values within artist's indivdual JSON
	    for x in dump_new[a]:
	        try:
	            metric_type = x['Service']['name'].encode('ascii', errors = 'ignore')
	            new_dict = dict()
	            
	            try:
	                for key in x['Metric']:
	                    ####CHECK IF THIS IS RIGHT 
	                    if type(x['Metric'][key]) != list: 
	                        days_values = []
	                        for day, value in x['Metric'][key].iteritems():
	                            c_key = np.int16(day).astype('datetime64[D]')
	                            days_values.append((str(c_key),value))
	                        new_dict[key] = days_values   
	                    else:
	                        new_dict[key] = x['Metric'][key]
	                dict_types[metric_type] = new_dict
	                ## add the remaining elements of the json - need the keys
	                dict_types[metric_type].update([x['Profile'], x['Service']])
	            except Exception, e:
	                print x['Metric']
	                print 'error ' , e[0]
	        except Exception , e:
	           print 'Error: ', e[0]
	           print 'bad ... ', x
	    converted_nbs[a.encode('ascii', errors = 'ignore').rstrip()] = dict_types
	  return converted_nbs

if __name__ == '__main__':
	main()

	conn = psyco.connect(dbname = 'nebulae')
	engine = create_engine('postgresql://dubT:!@localhost:5432/nebulae')

	new_guys, new_parms = getBillboard()
	emerge_bill = pd.read_sql('billboard_emerge', engine)
	cur_arts = set(emerge_bill['name'])
	needed = new_guys - cur_arts

	cur = conn.cursor()
	query = 'insert into billboard_emerge(name) values (%s)'
	for art in list(needed):
	    
	    cur.execute(query, (art,))
	conn.commit()

	cur.execute('select distinct artist from static_labeled')
	current = cur.fetchall()
	current =  [x[0] for x in current]
	needed = set(new_guys) - cur_arts

	more_eco = []
	for x in needed:
	    
	    if x not in current:
	        more_eco.append(x.rstrip())

	cur = conn.cursor()

	query = 'insert into static_labeled(b_emerging, artist, discovery, familiarity, hottness, p_rising ) values (%s, %s, %s, %s, %s, %s)'
	for x in new_guys:
	    cur.execute(query, (1, x['artist']['name'], x['artist']['discovery'], x['artist']['familiarity'], x['artist']['hotttnesss'], 0,))
	conn.commit()
