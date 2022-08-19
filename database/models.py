from email.policy import default
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    Boolean,
    String
)
from datetime import datetime
import time

from database.base import Base


def datetime_to_unix():
    return int(time.mktime(datetime.now().timetuple()))


# users tables
class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)

    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    is_loading = Column(Boolean, nullable=False, default=False)
    loads = Column(Integer, nullable=False, default=0)

    last_action_date = Column(Integer, default=datetime_to_unix(), nullable=False, index=True)
    updated_at = Column(Integer, default=datetime_to_unix(), nullable=False, index=True)
    created_at = Column(Integer, default=datetime_to_unix(), nullable=False, index=True)

