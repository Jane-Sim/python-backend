# SQLAlchemy를 통해 mariaDB연결과 
# ORM으로 DB테이블들을 파이썬 클래스와 매핑시킵니다.

# SQLAlchemy에서 컬럼, 스트링, 인트 등의 모듈들을 불러옵니다.
from sqlalchemy import Column, String, Integer, text, ForeignKeyConstraint
# SQLAlchemy에서 mysql에서 사용하는 TIMESTAMP 모듈을 불러옵니다.
from sqlalchemy.dialects.mysql import TIMESTAMP
 # SQLAlchemy에서 테이블간의 관계를 파이썬이 이해할 수있도록 클래스 연결 모듈들을 불러옵니다.
from sqlalchemy.orm import relationship
# 기존에 연결해놓은 DB를 불러옵니다.
from sqlalchemy.ext.declarative import declarative_base
# declarative_base 함수를 통해 기반 클래스 생성.
from . import Base

from .users import Users

# 사용자들의 트윗들을 저장하는 테이블.
class Tweets(Base):
    __tablename__ = 'tweets'

    # 트윗을 쓰는 유저아이디와 트윗, 생성일, 유저아이디에 대한 외래키를 설정한다.
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column('user_id', Integer, nullable=False)
    tweet = Column('tweet', String(300), nullable=False)
    created_at = Column('created_at', TIMESTAMP, nullable=False, server_default=text('NOW()'))
    tweets_user_id_fkey = ForeignKeyConstraint(
                                    ['user_id'], ['users.id'],
                                    name = 'tweets_user_id_fkey')
    user = relationship("Users", primaryjoin=
                                    user_id==Users.id,
                                    foreign_keys=user_id)

                                    
    
    def __init__(self, user_id, tweet):
        self.user_id = user_id
        self.tweet = tweet