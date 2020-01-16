# 데이터베이스와 DB에 연결하는 URL 정보를 담은 config 파일.

# DB를 연결하는 정보를 담은 배열
db = {
    'user' : 'UserID',
    'password' : 'writePW',
    'host' : 'WriteHostDB.ap-northeast-2.rds.amazonaws.com',
    'port' : 0000,
    'database' : 'DB_Name'
}

# DB URL
DB_URL = f"mysql+mysqldb://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

# 유저의 비밀번호를 암/복호화를 위한 JWT secret 키
JWT_SECRET_KEY = 'WriteSecretKey'

# TEST DB를 연결하는 정보를 담은 배열
test_db = {
     'user' : 'UserTestID',
    'password' : 'writePW',
    'host' : 'WriteTestHostDB.ap-northeast-2.rds.amazonaws.com',
    'port' : 0000,
    'database' : 'DB_Name'
}

# TEST DB URL
test_config = {
    'DB_URL' : f"mysql+mysqldb://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY' : 'WriteSecretKey'
}

