import blogged_collection as bc
from sqlalchemy import create_engine

def main():

<<<<<<< HEAD
	engine = create_engine('postgresql://postgres:hype@ip-172-31-3-213:5432/hypemerdb')
=======
	conn = psyco.connect(dbname = 'hypemerdb')
	cur = conn.cursor()
>>>>>>> 48afb81141289b21559dcf7a05dd02016df0178e
	
	blogd = bc.hypem_emergence(5)

	query = 'insert into hypemer_closet( artist, result, img ) values (%s, %s, %s)'
	for x in blogd.features[['Results', 'img']].iterrows():
	    cur.execute(query, (x[0], x[1][0], x[1][1],))
	#blogd.features[['Results', 'img']].to_sql('hypemer_closet', engine, if_exists='append')
	conn.commit()

if __name__ == '__main__':
	main()
