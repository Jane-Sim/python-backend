# 동기식으로 처리되는 flask 앱을 향상시키기 위해,
# 비동기식으로 멀티요청이 가능한 twisted 웹서버 라이브러리를 사용합니다.

# flask로 만든 웹서버를 twisted 안에 넣음으로써 더욱 많은 요청들을 처리할 수 있습니다.

import sys

from flask_script import Manager
from app import create_app
from flask_twisted import Twisted
from twisted.python import log

if __name__ == "__main__":
    app = create_app()

    twisted = Twisted(app)
    log.startLogging(sys.stdout)

    app.logger.info(f"Running the app...")
    
    manager = Manager(app)
    manager.run()