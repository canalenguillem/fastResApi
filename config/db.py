from sqlalchemy import create_engine,MetaData

create_engine("mysql+pymysql://root:root@localhost:3306/storedb")