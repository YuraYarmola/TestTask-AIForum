# AI FORUM TEST TASK
<hr>

## ABOUT
This is simple system where user can auth by email and password. Create and modify posts, create comments and make reply for them. The main idea, was that it automatically moderate for toxic words, and can automatically reply for comments from autor with GPT.
<hr>

### Project run with docker

1. Install Docker
2. Make .env file with your credentials variables from example
3. run <code>docker compose build</code>
4. run <code>docker compose up -d</code>

You can use postmen collection to test it


### TESTS

To run tests you need to:
1. Make and activate venv
2. Make .env file from example
3. Install requirements <code>pip install -r requirements.txt</code>
4. Make migrate <code>python manage.py migrate</code>
5. Run test <code>python manage.py test</code>