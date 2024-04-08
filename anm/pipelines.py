import os
from itemadapter import ItemAdapter
from .items import AnmItem, EpItem
from .models import Base, Anime, Ep
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import PendingRollbackError
from dotenv import load_dotenv
load_dotenv()


class AnmPipeline:
    def __init__(self) -> None:
        uri = str(os.getenv('DB_URI')) + "?sslmode=require"
        self.engine = create_engine(uri, echo=True)
        
        self.tables = ['anime', 'episode']
        self._create_tables()

        self.session = sessionmaker(self.engine)
    
    def _create_tables(self):
        for table in self.tables:
            Base.metadata.tables[table].create(self.engine, checkfirst=True)
        
    def open_spider(self, spider):
        if not hasattr(self, 'dbsession'):
            self.dbsession = self.session()
            spider.logger.info('\033[41m CONEXÃO COM BANCO DE DADOS ABERTA\033[m')

    def process_item(self, item, spider):
        try:
            if isinstance(item, AnmItem):
                anime = Anime(
                    **ItemAdapter(item).asdict()
                )
                self.dbsession.add(anime)
                self.dbsession.commit()
            
            elif isinstance(item, EpItem):
                ep = Ep(
                    **ItemAdapter(item).asdict()
                )

                self.dbsession.add(ep)
                self.dbsession.commit()

        except PendingRollbackError as e:
            spider.logger.warning(f'\033[33m{e}\033[m')
            if hasattr(self, 'dbsession'):
                self.dbsession.rollback()
        
        finally:
            return item

    def close_spider(self, spider):
        if hasattr(self, 'dbsession'):
            self.dbsession.close()
            spider.logger.info('\033[42m CONEXÃO COM BANCO DE DADOS FECHADA \033[m')
