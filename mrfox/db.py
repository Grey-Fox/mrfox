from contextlib import contextmanager

from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class DB(object):
    def __init__(self, uri):
        self._engine = create_engine(uri)

    def get_session(self):
        return orm.sessionmaker(bind=self._engine)()

    def get_conn(self):
        return self._engine.connect()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def engine(self):
        return self._engine


def init_db(db):
    Base.metadata.create_all(db.engine)


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer,
                primary_key=True,
                nullable=False)
    external_id = Column(Integer,
                         nullable=False)
    first_name = Column(Text)
    last_name = Column(Text)

    def __repr__(self):
        return '<Clientl {}: {} {}>'.format(
            self.external_id, self.first_name, self.last_name
        )
