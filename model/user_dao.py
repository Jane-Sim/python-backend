# 유저에 대한 정보를 저장하고 불러오는 modle layer 파일입니다.

# contextmanager 를 통해서, 세션을 생성하구 커밋, 종료를 반복하지 않고
# 재사용할 수 있게끔 사용해줍니다.
from contextlib import contextmanager

Session = None

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

# 해당 유저 로직에 필요한 user, followList ORM 을 상속받습니다. 
class UserDao:
    def __init__(self, session, userORM, user_follow_listORM):

        global Session
        Session =  session
        self.Users = userORM
        self.UsersFollowList = user_follow_listORM

    # 새로운 유저를 DB에 저장하는 함수
    def insert_user(self, user):
        # 유저에게 받은 json 데이터를 Users 클래스로 매핑시킵니다.
        new_user = self.Users(user['name'],user['email'],user['password'],user['profile'])
        
        # DB 세션을 통해 새로운 유저데이터를 저장.
        # flush 를 통해 add한 데이터를 DB에 적용시켜서, 해당 데이터에 대한 last row id 값을 가져옵니다.
        with session_scope() as session:        
            session.add(new_user)
            session.flush()

            return new_user.id

    # 이메일을 통해 id 와 pw 를 가져오는 함수
    def get_user_id_and_password(self, email):
        with session_scope() as session:
            # 로그인하는 유저의 이메일과 매칭되는 DB에 저장된 유저의 데이터를 가져온다.
            row = session.query(self.Users.id, self.Users.hashed_password).filter(self.Users.email == email).first()

            return {
                'id' : row.id,
                'hashed_password' : row.hashed_password
            } if row else None

    # 유저의 팔로우 요청을 저장합니다.
    def insert_follow(self, user_id, follow_id):
        with session_scope() as session:        
            newFollow = self.UsersFollowList(user_id, follow_id)
            session.add(newFollow)

            return True

    # 사용자가 언팔로우한 요청을 찾아 삭제 후 저장.
    def insert_unfollow(self, user_id, unfollow_id):
        with session_scope() as session:
            user = session.query(self.UsersFollowList).filter(self.UsersFollowList.user_id == user_id, self.UsersFollowList.follow_user_id == unfollow_id).first()
            if user:
                session.delete(user)
                return True
            else:
                return False