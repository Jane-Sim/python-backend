# 트윗을 저장하고 타임라인 리스트를 가져오는 트윗 service layer입니다.

class TweetService:

    def __init__(self, tweet_dao):
        self.tweet_dao = tweet_dao

    # 트윗이 300자가 넘을 떄, None을 반환합니다.
    def tweet(self, user_id, tweet):
        if len(tweet) > 300:
            return None
        
        return self.tweet_dao.insert_tweet(user_id, tweet)

    # 타임라인 리스트를 반환합니다.
    def get_timeline(self, user_id):
        return self.tweet_dao.get_timeline(user_id)