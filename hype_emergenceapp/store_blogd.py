import blogged_collection as bc
from sqlalchemy import create_engine

def main():

	conn = psyco.connect(dbname = 'hypemerdb')
	cur = conn.cursor()
	
	blogd = bc.hypem_emergence(5)

	query = 'insert into hypemer_closet( artist, result, img ) values (%s, %s, %s)'
	for x in blogd.features[['Results', 'img']].iterrows():
	    cur.execute(query, (x[0], x[1][0], x[1][1],))
	#blogd.features[['Results', 'img']].to_sql('hypemer_closet', engine, if_exists='append')
	conn.commit()

if __name__ == '__main__':
	main()