# Ziggly | Simple Stock Management Application

## Installation
Clone the repository
```sh
git clone https://github.com/jkalasas/ziggly.git
```
Create a python virtual environment and install dependencies
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create an .env file and fill the required environment variables
```
FLASK_APP=
FLASK_ENV=
CONFIG_TYPE=
BIND_ADDRESS=
```
Start application
```sh
gunicorn -c gunicorn.conf.py
```

## Notable Features
- Inventory Management
- Login System
- Cashier Mode