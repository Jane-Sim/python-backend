# 사용자를 저장하고 로그인, 보안인증, 액세스토큰 생성, 언/팔로우를 할 수 있는 유저 service layer입니다.

# 사용자의 비밀번호를 단방향 암호화하기 위해 bcrypt 해시 함수를 추가한다.
import bcrypt
# 사용자의 access token을 json 데이터로 보내기 위한 jwt 모듈을 추가한다.
import jwt

# 토큰을 생성할 때 토큰 유효기간을 지정하는 datetime 라이브러리
from _datetime import datetime, timedelta

class UserService:

    # 유저의 데이터를 저장해주는 model layer를 상속받습니다.
    def __init__(self, user_dao, config):
        self.user_dao = user_dao
        self.config = config

    # 유저를 생성하는 함수
    def create_new_user(self, new_user):
        # 유저의 비밀번호를 단방향 암호화기능인 bcrypt를 사용해 암호화시킵니다.
        # hashpw : 암호화로 만드는 함수. 1. 암호화하고자하는 byte와 2. 암호화하고자하는 salting을 추가하여 함호화시킨다.
        # encode('UTF-8') : string 데이터를 UTF-8로 인코딩하여 byte로 변경합니다.
        new_user['password'] = bcrypt.hashpw(
            new_user['password'].encode('UTF-8'), 
            bcrypt.gensalt()
        )

        new_user_id = self.user_dao.insert_user(new_user)

        return new_user_id

    # 로그인 함수
    def login(self, credential):
        email = credential['email']
        password = credential['password']

        print(f"유저가 입력한 {email} 과 {password}")
        # 로그인하는 유저의 이메일과 매칭되는 DB에 저장된 유저의 데이터를 가져온다.
        user_credential = self.user_dao.get_user_id_and_password(email)

        # 매칭되는 유저가 있으면 해당 유저의 비밀번호와 로그인한 유저의 비밀번호값이 일치하는지 비교한다.
        # bcrypt.checkpw로 로그인한 비밀번호를 암호화하여, DB에서 꺼내온 유저의 비밀번호와 일치하는지 bcrypt이 기능을 수행해준다. 
        authorized = user_credential and bcrypt.checkpw(password.encode('UTF-8'), user_credential['hashed_password'].encode('UTF-8'))
        
        return authorized

    # 찾고자하는 유저정보를 이메일 정보를 통해 꺼내온다.
    def get_user_id_and_password(self, email):
        return self.user_dao.get_user_id_and_password(email)

    # 액세스토큰을 생성하는 함수
    def generate_access_token(self, user_id):

        payload = {
                    'user_id' : user_id,
                    'exp' : datetime.utcnow() + timedelta(seconds = 60 * 60 * 24)
                }
        # jwt.encode를 통해 최초의 토큰을 인증하기 위해 인코딩을 한다.
        # 보내고자하는 payload 데이터와 jwt secret 키, 해시키를 넣어준다. 
        token = jwt.encode(payload, self.config['JWT_SECRET_KEY'], 'HS256')

        # 해당 액세스 토큰을 사용자에게 보내준다.
        return token.decode('UTF-8')

    # 팔로우 기능
    def follow(self, user_id, follow_id):
        return self.user_dao.insert_follow(user_id, follow_id)
        
    #언팔로우 기능
    def unfollow(self, user_id, unfollow_id):
        return self.user_dao.insert_unfollow(user_id, unfollow_id)