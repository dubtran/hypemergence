import blogged_collection as bc
from sqlalchemy import create_engine

def main():

	engine = create_engine('postgresql://dubT:unicorn!@localhost:5432/nebulae')
	
	blogd = bc.hypem_emergence(1)
	blogd.for_show[['probas', 'img', 'soundcloud']].to_sql('hypemer_trunk', engine, if_exists='replace')


if __name__ == '__main__':
	main()