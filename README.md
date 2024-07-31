# AI FORUM TEST TASK

project run with docker

1. Install Docker
2. Make .env file with your credentials variables
3. run <code>docker compose build</code>
4. run <code>docker compose up -d</code>

You can use postgres collection to test it


### TESTS

To run tests you need to:
1. Make and activate venv
2. Make .env file from example
3. Install requirements <code>pip install -r requirements.txt</code>
4. Make migrate <code>python manage.py migrate</code>
5. Run test <code>python manage.py test</code>