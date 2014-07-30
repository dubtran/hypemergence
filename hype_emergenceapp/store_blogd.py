import blogged_collection as bc
from sqlalchemy import create_engine

'''
Main python script to create a hypem_emergence object that scrapes 3 pages of artists, 
collects their data, featurize the data, run the model, and stores the results into a postgres 
database for later use by HypeMergence.
'''

def main():

	engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')
	
	#The number given here can be changed to increase the number of artists appearing on HypeMergence
	blogd = bc.hypem_emergence(3)
	blogd.for_show[['probas', 'img', 'soundcloud']].to_sql('hypemer_trunk', engine, if_exists='replace')


if __name__ == '__main__':
	main()
