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

# 사용자가 다른 사용자를 팔로우, 언팔로우할 때 사용되는 팔로우리스트 테이블.
class UsersFollowList(Base):
    __tablename__ = 'users_follow_list'

    # 현재 유저와 팔로우하는 유저의 id를 지정하고, 생성일자와 id값들의 외래키에 대한 설정을 지정해준다.
    user_id = Column('user_id', Integer, primary_key=True, nullable=False)
    follow_user_id = Column('follow_user_id', Integer, primary_key=True, nullable=False)
    created_at = Column('created_at', TIMESTAMP, nullable=False, server_default=text('NOW()'))
    users_follow_list_user_id_fkey = ForeignKeyConstraint(
                                    ['user_id'], ['users.id'],
                                    name = 'users_follow_list_user_id_fkey')
    users_follow_list_follow_user_id_fkey  = ForeignKeyConstraint(
                                    ['follow_user_id'], ['users.id'],
                                    name = 'users_follow_list_follow_user_id_fkey')
    user = relationship("Users", primaryjoin=
                                    user_id==Users.id,
                                    foreign_keys=user_id)
    follow_user = relationship("Users", primaryjoin=
                                    follow_user_id==Users.id,
                                    foreign_keys=follow_user_id)

    def __init__(self, user_id, follow_user_id):
        self.user_id = user_id
        self.follow_user_id = follow_user_id