# 데이터베이스와 DB에 연결하여 데이터 입력, 수정을 확인하는  TEST model unit config 파일.
# 1. pytest는 test_ 로 시작하는 파일들만 인식한다.
# 2. 마찬가지로 유닛테스트 파일의 함수들도 test_ 로 시작되어야한다.
# 3. setup_function과 teardown_function을 이용하면 각 test 함수들이 실행 되기 전에 필요한 데이터들을 생성, 삭제해준다.
#   - setup_function은 테스트 함수가 실행되기 전 먼저 시작되는 함수이며,
#   - teardown_function은 테스트 함수가 실행이 끝나고, 후에 시작되는 함수이다.
# flask의 test_client 함수를 통해 엔드포인트 함수들에 가상의 HTTP 요청을 보내고 응답을 받을 수 있다.

# 데이터베이스의 정보가 담긴 config 파일
import config
# 비밀번호를 암호화시켜주는 bcrypt
import bcrypt
# 유닛테스트에 필요한 pytest 라이브러리
import pytest
# DBORM 들을 불러온다.
from repository import Base, Users, Tweets, UsersFollowList
# DB에 데이터를 저장하는 로직들
from model import UserDao, TweetDao
# sqlalchemy의 엔진을 만드는 함수
from sqlalchemy import create_engine
# sqlalchemy를 통해 디비와 연결이 끊기지 않고, 트랜젝션을 관리하는 세션을 만드는 sessionmaker(세션공장).
from sqlalchemy.orm import sessionmaker

# contextmanager 를 통해서, 세션을 생성하구 커밋, 종료를 반복하지 않고
# 재사용할 수 있게끔 사용해줍니다.
from contextlib import contextmanager

# 위에서 적용한 config에서 DB URL을 통해 sqlalchemy 엔진을 생성.
engine = create_engine(config.test_config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

# 위의 엔진을 통해 세션을 생성한다.
Session = sessionmaker(bind=engine)

# Base를 상속받은 db class들을 mariaDB 관계형 디비 테이블들과 매핑하여 웹서버에 적용시킵니다.
Base.metadata.create_all(engine)

# contextmanager 데코레이션을 사용해 try/finally이 재사용가능한 
# session_scope함수를 만들고, with 문을 통해서 해당 함수를 불러온다.
@contextmanager
def session_scope():
    # SQLAlchemy 의 세션을 global하게 사용안하게끔 멀티스레드처럼 세션들을 생성한다.
    session = Session()
    try:
        #yield 로 생성한 session을 전달합니다.
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# 유닛 테스트에서는 실제 서비스가 동작되지 않아서, test 함수들에 인자를 넘겨줄 수 없지만,
# pytest.fixture를 사용하면, pytest가 자동으로 지정된 인자와 동일한 이름에 
# pytest.fixture decorator가 적용된 함수를 찾아서 리턴 값을 test 함수에 적용시켜준다.
# 유저 DB로직과 트윗 DB로직을 불러온다. 
@pytest.fixture
def user_dao():
    return UserDao(Session, Users, UsersFollowList)

@pytest.fixture
def tweet_dao():
    return TweetDao(Session, Tweets, UsersFollowList)

# 테스트 함수가 실행되기 전 먼저 시작되는 함수
# 각 test 함수들이 실행 되기 전에 필요한 데이터들을 생성 (회원가입)
def setup_function():
    ##Create a test user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )

    ##테스트 사용자 생성
    with session_scope() as session:
        session.add_all([
            Users('송은우','songew@gmail.com',hashed_password,'test profile'),
            Users('김철수','tet@gmail.com',hashed_password,'test profile')])
        session.add(Tweets(2, "Hello World!"))

# 테스트 함수가 실행이 끝나고, 후에 시작되는 함수
# 테스트 데이터베이스의 3개의 테이블을 비워내는 역할.
def teardown_function():
    with session_scope() as session:
        session.execute('''SET FOREIGN_KEY_CHECKS=0''')
        session.execute('''TRUNCATE TABLE users''')
        session.execute('''TRUNCATE TABLE tweets''')
        session.execute('''TRUNCATE TABLE users_follow_list''')
        session.execute('''SET FOREIGN_KEY_CHECKS=1''')

# 유저의 id로 유저정보를 가져온다.
def get_user(user_id):
    with session_scope() as session:
        user = session.query(Users.id, Users.name, Users.email, Users.profile).filter(Users.id == user_id).first()
        
        return {
            'id':user.id,
            'name':user.name, 
            'email':user.email,
            'profile': user.profile
        } if user else None

# 유저 id로 팔로우한 유저리스트를 불러온다. 이 떄, 유저의 id값만 리스트에 넣는다.
def get_follow_list(user_id):
    with session_scope() as session:
        rows = session.query(UsersFollowList.follow_user_id).filter(UsersFollowList.user_id == user_id).all()
        
        return [int(r.follow_user_id) for r in rows]

# 새로운 유저를 저장하고, 해당 유저를 id 값으로 제대로 불러오는지 테스트
def test_insert_user(user_dao):
    new_user = {
        'name':'홍길동', 
        'email':'hong@test.com',
        'profile':'서쪽에서 번쩍, 동쪽에서 번쩍', 
        'password':'test1234'
    }
    new_user_id = user_dao.insert_user(new_user)
    user = get_user(new_user_id)

    assert user == {
        'id' : new_user_id,
        'name' : new_user['name'],
        'email' : new_user['email'],
        'profile' : new_user['profile']
    }

def test_get_user_id_and_password(user_dao):
    ## get_user_id_and_password 메소드를 호출하여; 사용자의 아이디와 비밀번호 해시 값을 읽어 들인다.
    ## 사용자는 이미 setup_function에서 생성된 사용자를 사용한다.
    user_credential = user_dao.get_user_id_and_password(email = 'songew@gmail.com')

    ##먼저 사용자 아이디가 맞는지 확인한다.
    assert user_credential['id'] == 1

    ##그리고 사용자 비밀번호가 맞는지 bcrypt의 checkpw 메소드를 사용해서 확인한다.
    assert bcrypt.checkpw('test password'.encode('UTF-8'), user_credential['hashed_password'].encode('UTF-8'))

def test_insert_follow(user_dao):
    ## insert_follow 메소드를 사용하여 사용자 1이 사용자 2를 팔로우하도록 한다.
    ## 사용자 1과 2는 setup_function에서 이미 생성되었다.
    user_dao.insert_follow(user_id = 1, follow_id = 2)

    follow_list = get_follow_list(1)

    assert follow_list == [2]

def test_insert_unfollow(user_dao):
    ## insert_follow 메소드를 사용하여 사용자 1이 사용자 2를 팔로우한 후 언팔로우한다.
    ## 사용자 1과 2는 setup_function에서 이미 생성되었다.
    user_dao.insert_follow(user_id = 1, follow_id = 2)
    user_dao.insert_unfollow(user_id = 1, unfollow_id = 2)

    follow_list = get_follow_list(1)

    assert follow_list == [ ]

# 트윗이 제대로 저장되는지, 불러와지는지 테스트
def test_insert_tweet(tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id' : 1,
            'tweet' : 'tweet test'
        }
    ]

# 유저 1과 2가 트윗을 입력 후, 1이 2를 팔로우한 뒤,
# 미리 입력했던 유저 2의 트윗과 새로입력한 1과 2의 트윗을 잘 불러오는지 테스트.
def test_timeline(user_dao, tweet_dao):
    tweet_dao.insert_tweet(1, "tweet test")
    tweet_dao.insert_tweet(2, "tweet test 2")
    user_dao.insert_follow(1, 2)

    timeline = tweet_dao.get_timeline(1)

    assert timeline == [
        {
            'user_id' : 2,
            'tweet' : 'Hello World!'
        },
        {
            'user_id' : 1,
            'tweet' : 'tweet test'
        },
        {
            'user_id' : 2,
            'tweet' : 'tweet test 2'
        }
    ]