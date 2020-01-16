# SQLAlchemy를 통해 관계형DB 테이블을 파이썬 클래스로 매핑시킨 repository ORM 파일입니다.
# Base 기능을 init 파일에 넣음으로, 각 클래스를 생성할 때 해당 Base를 상속받게합니다.

# declarative_base 함수를 통해 기반 클래스 생성.
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .users import Users
from .tweets import Tweets
from .users_follow_list import UsersFollowList

__all__ = [
    'Users',
    'Tweets',
    'UsersFollowList'
]