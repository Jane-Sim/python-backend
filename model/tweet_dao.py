# 유저의 트윗을 저장하고 불러오는 modle layer 파일입니다.

# sqlalchemy 를 사용하는데 필요한 or 문과 별칭인 aliased 를 추가합니다.
from sqlalchemy import or_
from sqlalchemy.orm import aliased

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

# 해당 트윗 로직에 필요한 tweet, followList ORM 을 상속받습니다. 
class TweetDao:
    def __init__(self, session, tweetsORM, user_follow_listORM):
        global Session
        Session =  session
        self.Tweets = tweetsORM
        self.UsersFollowList = user_follow_listORM

    # 사용자의 트윗을 저장하는 함수
    def insert_tweet(self, user_id, tweet):
        with session_scope() as session:        
            tweet = self.Tweets(user_id, tweet)
            session.add(tweet)

            return True

    # 사용자의 타임라인을 가져오는 함수
    def get_timeline(self, user_id):
        # 깔끔한 쿼리문을 위해, 두 테이블에 별칭을 달아줍니다.
        t = aliased(self.Tweets)
        ufl = aliased(self.UsersFollowList)

        # 트윗 테이블의 유저아이디와 트윗 내용으로 데이터를 가져옵니다.
        # 왼쪽 조인으로 해당 유저가 팔로우리스트가 비었어도 
        # 해당 유저의 트윗은 전부 가져올 수 있도록 전체 트윗 데이터를 가져옵니다.
        # 이때, where절에 해당 유저의 id와 팔로우한 유저의 id로만 트윗을 가져오게 설정합니다.
        with session_scope() as session:
            timeline = session.query(t.user_id, t.tweet).\
                        outerjoin(ufl, ufl.user_id == user_id).\
                        filter(or_(t.user_id == user_id, t.user_id == ufl.follow_user_id)).all()
        
            # 가져온 트윗 데이터를 타임라인배열로 매핑한 뒤, 클라이언트에 반환해줍니다.
            return [{
                'user_id' : tweet.user_id,
                'tweet' : tweet.tweet
            } for tweet in timeline]
