import blogged_collection as bc
from sqlalchemy import create_engine
import psycopg2 as psyco

def main():

	engine = create_engine('postgresql://ubuntu:hype@localhost:5432/hypemerdb')
	conn = psyco.connect(database='hypemerdb') 
	cur = conn.cursor()
	
	blogd = bc.hypem_emergence(5)

	blogd.features[['probas', 'img', 'soundcloud']].to_sql('hypemer_trunk', engine, if_exists='replace')
	conn.commit()

if __name__ == '__main__':
	main()
