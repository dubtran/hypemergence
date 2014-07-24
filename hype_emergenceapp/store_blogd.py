import blogged_collection as bc
from sqlalchemy import create_engine

def main():

	engine = create_engine('postgresql://postgres:hype@ip-172-31-3-213:5432/hypemerdb')
	
	blogd = bc.hypem_emergence(5)
	blogd.features[['Results', 'img']].to_sql('hypemer_closet', engine, if_exists='append')


if __name__ == '__main__':
	main()
