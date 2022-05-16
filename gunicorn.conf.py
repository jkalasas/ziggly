import multiprocessing
import os
from dotenv import load_dotenv

for env_file in ('.env', '.flaskenv'):
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)

wsgi_app = 'app:app'
bind = os.getenv('BIND_ADDRESS', '127.0.0.1:3000')
workers = multiprocessing.cpu_count() * 2 + 1