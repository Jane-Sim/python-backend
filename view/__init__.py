# 클라이언트의 요청을 받는 View layer입니다.
# 사용자들의 액세스 토큰을 확인함으로써, 보안인증을 할 수 있으며
# 라우터 기능을 사용해 각 엔드포인트마다 사용자의 요청을 구분합니다.

# 사용자의 access token을 json 데이터로 보내기 위한 jwt 모듈을 추가한다.
import jwt
# 플라스크의 모듈들을 불러온다. flask 로 서버를 만들고, jsonify로 데이터를 json로 쉽게 매핑해서 클라이언트에 전달,
# request 를 통해 클라이언트에서 보낸 데이터를 json 데이터로 받는다.
from flask import jsonify, request, Response, current_app, g
# JSONEncoder 를 통해서, 클라이언트가 보낸 json이 아닌 데이터들도 json인코더를 통해 json 데이터로 받는다. 
from flask.json import JSONEncoder
# decorator 함수를 만들 때, 부차적으로 생기는 이슈를 해결해주는 wraps decorator 함수를 추가한다.
from functools import wraps

# 해당 함수는 flask에서 Json으로 인코딩을 할 때, json이 아닌 set을 클라이언트에서 받아도,
# json으로 인식할 수 있도록 set을 list로 변경해주는 함수.
class CustomJSONEncoder (JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

# 로그인확인 decorator 함수를 지정한다.
# 해당 login_required decorator함수가 지정된 함수는 해당 사용자가 로그인이 되어있어야 실행된다.
# 해당 decorator 함수를 적용시킨 함수를 가져와 (f) login_required decorator 에 적용한 내용을 먼저실행 후 f 를 실행시킨다. 
def login_required (f):
    # wraps decorator 함수를 적용해 이슈처리를 해결하게 한다.
    @wraps(f)
    # 해당 함수가 모든 인자값을 받을 수 있도록 *args 와 **kwargs를 적용시킨다.
    def decorated_function(*args, **kwargs):
        # 액세스토큰을 클라이언트의 요청값의 헤더부분의 Authorization에서 가져온다.
        access_token = request.headers.get('Authorization')
        print(access_token)
        # 액세스토큰이 있으면, 해당 토큰을 jwt로 복호화해서 유저아이디를 구한다.
        if access_token is not None:
            try: #토큰을 복호화할 때 사용한 secret키와 해시값을 적용한다.
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            # 토큰을 복호화하다가 오류나면, payload를 None으로 적용시킨다.
            except jwt.InvalidTokenError:
                payload = None
            # payload가 None일 때, 클라이언트에 인증 오류를 전달한다.
            if payload is None : 
                print('인증오류') 
                return Response(status=401)

            # 토큰을 통해 얻음 유저아이디로 DB에서 유저정보를 가져오고, 글로벌하게 유저정보를 넣어준다.
            user_id = payload['user_id']
            g.user_id = user_id
        # 토큰이 없으면 인증 오류를 날린다.
        else: 
            print('인증 오류2')
            return Response(status = 401)
        #마지막으로 decorated_function 을 적용한 함수를 실행시킨다.
        return f(*args, **kwargs)
    return decorated_function

# 해당 View layer를 실행시키는 함수입니다.
# 상속받은 flask app을 통해 라우터 기능을 사용하며
# 비즈니스 로직을 담당하는 user, tweet 서비스를 사용합니다.
def create_endpoints(app, services):
    app.json_encoder = CustomJSONEncoder

    user_service = services.user_service
    tweet_service = services.tweet_service

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    # 회원가입을 할 때 사용하는 함수
    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        # 새로 가입한 사용자정보를 받음.
        newUser = request.json
       
        # 새 유저의 데이터를 유저서비스에 보내어 저장합니다.
        new_user = user_service.create_new_user(newUser)

        if new_user : return jsonify(new_user) 
        elif new_user is None  : return '해당 유저가 존재하지 않습니다.', 400
        else : return '유저를 찾아오던 중 오류가 발생했습니다.', 500

    # 로그인할 때 사용하는 함수
    @app.route("/login", methods=['POST'])
    def login():
        # 사용자의 로그인데이터를 받는다. email이 아이디입니다. Unique key를 설정했기에, 중복X.
        credential = request.json
        email = credential['email']
        password = credential['password']

        #print(f"유저가 입력한 {email} 과 {password}")

        # 사용자가 입력한 로그인 데이터를 통해, DB에서 해당 유저가 있는지 확인합니다. Boolean
        authorized = user_service.login(credential)

        # 사용자가 있다면, 해당 유저의 아이디로 pk 값인 id를 가져오며,
        # id 값을 통해 액세스토큰을 만듭니다.
        if authorized:
            user_credential = user_service.get_user_id_and_password(credential['email'])
            user_id = user_credential['id']
            token = user_service.generate_access_token(user_id)
            # 유저의 아이디와 토큰을 클라이언트에 반환.
            return jsonify({
                'user_id' : user_id,
                'access_token' : token
            })
        else:
            return '', 401


    #트윗을 가져오는 route데코레이션
    @app.route('/tweet', methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        #로그인할 때 저장한 글로벌 변수를 통해 유저 아이디를 가져옵니다.
        user_id = g.user_id
        tweet = user_tweet['tweet']

        # 트윗을 저장합니다. 만약 300자를 초과해 저장했다면
        # 유저에게 400 에러 메세지를 보냅니다.
        result = tweet_service.tweet(user_id, tweet)
        if result is None:
            return '300자를 초과했습니다', 400

        return '', 200

    # 특정 유저를 팔로우하는 라우트데코레이션
    @app.route('/follow', methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        user_id = g.user_id
        follow_id = payload['follow']

        # 해당 요청이 성공적이면 200을 보낸다.
        if user_service.follow(user_id, follow_id) is True: return '', 200
        else: return '저장중 에러발생 [follow_user_id]', 500

    # 사용자를 언팔로우하는 라우트데코레이션
    @app.route('/unfollow', methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        user_id = g.user_id
        unfollow_id = payload['unfollow']

        # 사용자 언팔로우가 잘 적용되면 200을 전달한다.
        if user_service.unfollow(user_id,unfollow_id) is True: return '', 200
        else: return '해당 사용자가 없습니다.', 400

    # 타임라인을 가져오는 라우트데코레이션
    # 사용자의 로그인 유무를 확인하는 login_required 데코레이션
    @app.route('/timeline', methods=['GET'])
    @login_required
    def timeline():
        user_id = g.user_id
        timeline = tweet_service.get_timeline(user_id)

        # 가져온 트윗 데이터를 타임라인배열로 매핑한 뒤, 클라이언트에 반환해줍니다.
        return jsonify({
            'user_id' : user_id,
            'timeline' : timeline
        })

    return app

