# 파이썬 플라스크 라이브러리로 API 서버를 만드는 메인 서버파일.
# SNS 기능을 갖고있으며 유저는 회원가입, 로그인, 트윗작성, 팔로우, 언팔로우의 작업을 할 수 있다.
# SQLAlchemy를 통해 mariaDB와 연동해 데이터를 저장한다.

# 플라스크의 모듈들을 불러온다. flask 로 웹서버를 만든다.
from flask import Flask
# 백엔드와 다른 도메인 주소로 요청을 보낼 경우 생기는 CORS문제를 해결하기 위해 flask_cors에서 CORS 모듈을 추가
from flask_cors import CORS
# DB의 정보가 담긴 config 파일
import config 
# sqlalchemy의 엔진을 만드는 함수
from sqlalchemy import create_engine
# sqlalchemy를 통해 디비와 연결이 끊기지 않고, 트랜젝션을 관리하는 세션을 만드는 sessionmaker(세션공장).
from sqlalchemy.orm import sessionmaker

# 테이블ORM인 repository, 데이터를 저장하는 model layer
# 비즈니스 로직을 담당하는 service layer
# 클라이언트의 요청을 받는 view layer (route 기능 포함.)
from repository import Users, Tweets, UsersFollowList, Base
from model import UserDao, TweetDao
from service import UserService, TweetService
from view import create_endpoints

class Services:
    pass

# 처음 파이썬이 구동될 때 실행되는 함수.
# test_config 가 None일 경우 테스트버전이 아니므로, 실서버 config를 웹서버에 적용한다.
def create_app(test_config = None):

    # 플라스크로 웹서버를 만듭니다.
    app = Flask(__name__)
    #CORS를 웹서버에 적용
    CORS(app)

    # test_config가 None일 때는 실서버파일인 config.py파일을 app.config에 적용시킵니다.
    if test_config is None:
        app.config.from_pyfile("config.py")

    else:
        app.config.update(test_config)

    
    # 위에서 적용한 config에서 DB URL을 통해 sqlalchemy 엔진을 생성.
    engine = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

    # 위의 엔진을 통해 세션을 생성한다.
    Session = sessionmaker(bind=engine)

    # Base를 상속받은 db class들을 mariaDB 관계형 디비 테이블들과 매핑하여 웹서버에 적용시킵니다.
    Base.metadata.create_all(engine)

    ## ORM Layer
    userORM = Users
    tweetsORM = Tweets
    user_follow_listORM = UsersFollowList

    ## Persistence Layer
    user_dao = UserDao(Session, userORM, user_follow_listORM)
    tweet_dao = TweetDao(Session, tweetsORM, user_follow_listORM)

    ## Business Layer
    services = Services
    services.user_service = UserService(user_dao, app.config)
    services.tweet_service = TweetService(tweet_dao)

    ## 엔드포인트들을 생성
    create_endpoints(app, services)

    return app