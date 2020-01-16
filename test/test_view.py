# 데이터베이스와 DB에 연결하는 URL 정보를 담은 TEST unit config 파일.
# 1. pytest는 test_ 로 시작하는 파일들만 인식한다.
# 2. 마찬가지로 유닛테스트 파일의 함수들도 test_ 로 시작되어야한다.
# 3. setup_function과 teardown_function을 이용하면 각 test 함수들이 실행 되기 전에 필요한 데이터들을 생성, 삭제해준다.
#   - setup_function은 테스트 함수가 실행되기 전 먼저 시작되는 함수이며,
#   - teardown_function은 테스트 함수가 실행이 끝나고, 후에 시작되는 함수이다.
# flask의 test_client 함수를 통해 엔드포인트 함수들에 가상의 HTTP 요청을 보내고 응답을 받을 수 있다.

# 데이터베이스의 정보가 담긴 config 파일 (sqlalchemy 등)
import config
# 비밀번호를 암호화시켜주는 bcrypt
import bcrypt
# 유닛테스트에 필요한 pytest 라이브러리
import pytest
# 메인인 app에서 생성했던 create_app을 가져와서 해당 라우터들을 사용한다.
from app import create_app
# 유닛테스트에서 사용할 데이터들을 json으로 매핑시켜주는 json 모듈
import json
# model 파일에서 데이터베이스를 매핑한 클래스들을 불러온다.
from repository import Base, Users, Tweets, UsersFollowList
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
@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True

    # 가상의 HTTP 요청을 만든다. 
    # 엔드포인트 함수들에 가상의 HTTP 요청을 보내고 응답을 받을 수 있다.
    api = app.test_client()

    return api

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

# 핑퐁 엔드포인트로 테스트.
def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

# 가상의 유저가 로그인되는지 확인.
def test_login(api):
    
    ##로그인
    resp = api.post(
        '/login',
        data = json.dumps({'email' : 'songew@gmail.com',
        'password' : 'test password'}),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data
    
#access token이 없는 요청에 401 응답을 리턴하는지 테스트
def test_unauthorized(api):
    resp = api.post(
        '/tweet',
        data = json.dumps({'tweet' : "Hellow World!"}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp = api.post(
        '/follow',
        data = json.dumps({'follow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp = api.post(
        '/unfollow',
        data = json.dumps({'unfollow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

# 로그인 후 트윗을 작성할 수 있는지 테스트
def test_tweet(api):
    
    ##로그인
    resp = api.post(
        '/login',
        data = json.dumps({'email' : 'songew@gmail.com',
        'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']
    
    ## tweet
    resp = api.post(
        '/tweet',
        data = json.dumps({'tweet' : 'Hello World!'}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## tweet 확인
    resp = api.get(f'/timeline', headers = {'Authorization' : access_token})
    tweets = json.loads(resp.data.decode('UTF-8'))
    

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id' : 1,
                'tweet' : "Hello World!"
            }
        ]
    }

# 로그인 후 다른 유저를 팔로우 후, 팔로우한 유저의 트윗을 가져오는지 테스트
def test_follow(api):
    ##로그인
    resp = api.post(
        '/login',
        data = json.dumps({'email' : 'songew@gmail.com',
        'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']

    ## 먼저 사용자 1의 tweet 확인해서 tweet 리스트가 비어 있는 것을 확인
    resp = api.get(f'/timeline', headers = {'Authorization' : access_token})
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [ ]
    }

    # follow 사용자 아이디 = 2
    resp = api.post(
        '/follow',
        data = json.dumps({'follow':2}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 사용자 1의 tweet 확인해서 사용자 2의 tweet이 리턴되는 것을 확인
    resp = api.get(f'/timeline', headers = {'Authorization' : access_token})
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id' : 2,
                'tweet' : "Hello World!"
            }
         ]
    }

# 로그인 후 다른 유저를 팔로우 후, 다시 언팔로우하여 
# 언팔로우한 유저의 트윗을 안 갖고오는지 테스트.
def test_unfollow(api):
    # 로그인
    resp = api.post(
        '/login',
        data = json.dumps({'email' : 'songew@gmail.com',
        'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json = json.loads(resp.data.decode('UTF-8'))
    access_token = resp_json['access_token']

    # follow 사용자 아이디 = 2
    resp = api.post(
        '/follow',
        data = json.dumps({'follow':2}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 사용자 1의 tweet 확인해서 사용자 2의 tweet이 리턴되는 것을 확인
    resp = api.get(f'/timeline', headers = {'Authorization' : access_token})
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id' : 2,
                'tweet' : "Hello World!"
            }
         ]
    }

    # unfollow 사용자 아이디 = 2
    resp = api.post(
        '/unfollow',
        data = json.dumps({'unfollow':2}),
        content_type = 'application/json',
        headers = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 사용자 1의 tweet 확인해서 사용자 2의 tweet이 더 이상 리턴되지 않는 것을 확인
    resp = api.get(f'/timeline', headers = {'Authorization' : access_token})
    tweets = json.loads(resp.data.decode('UTF-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id' : 1,
        'timeline' : [ ]
    }