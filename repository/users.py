# SQLAlchemy를 통해 mariaDB연결과 
# ORM으로 DB테이블들을 파이썬 클래스와 매핑시킵니다.

# SQLAlchemy에서 컬럼, 스트링, 인트 등의 모듈들을 불러옵니다.
from sqlalchemy import Column, String, Integer, Date, text
# SQLAlchemy에서 mysql에서 사용하는 TIMESTAMP 모듈을 불러옵니다.
from sqlalchemy.dialects.mysql import TIMESTAMP
# 기존에 연결해놓은 DB를 불러옵니다.
from sqlalchemy.ext.declarative import declarative_base
# declarative_base 함수를 통해 기반 클래스 생성.
from . import Base

# 유저의 테이블을 클래스로 매핑시킵니다.
class Users(Base):
    __tablename__ = 'users'

    # 유저이름, 이메일, 비밀번호, 프로필, 생성일자, 업데이트 일자를 지정해줍니다.
    # 생성일자는 타임스탬프로 현재시간으로 저장해주고, 업데이트 일자는 빈값일때, 후에 해당 유저 데이터가 업데이트되면 현재시간으로 저장한다.
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column('name', String(255), nullable=False)
    email = Column('email', String(255), nullable=False, unique=True)
    hashed_password = Column('hashed_password', String(255), nullable=False)
    profile = Column('profile', String(2000), nullable=False)
    created_at = Column('created_at', TIMESTAMP, nullable=False, server_default=text('NOW()'))
    updated_at = Column('updated_at', TIMESTAMP, nullable=True, server_default=text('NULL ON UPDATE CURRENT_TIMESTAMP'))
    
    def __init__(self, name, email, hashed_password, profile):
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.profile = profile