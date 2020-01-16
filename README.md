# python-backend
파이썬 flask로 SNS 전용 API 백엔드서버를 만들었습니다. (토이프로젝트)

- 로그인, 회원가입, 언/팔로우, 글쓰기 등을 할 수 있으며, 로그인 보안 인증과 DB연동, ORM,
  MVC 패턴을 적용했으며 각 기능들을 테스트할 수 있도록 Unit Test를 만들었습니다.

1. 먼저 가상환경을 쉽게 관리해주는 miniconda 로 가상환경을 생성합니다.
2. 생성한 해당 가상환경으로 들어가서 명령어 "pip requirements.txt" 를 실행해 라이브러리 패키지들을 설치합니다.
3. "nohup python setup.py runserver --host=0.0.0.0 &" 명령어로 API 서버를 실행시킵니다.
