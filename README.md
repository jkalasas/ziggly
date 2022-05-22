# Ziggly | Simple Stock Management Application

## Installation
Clone the repository and cd to it
```sh
git clone https://github.com/jkalasas/ziggly.git && cd ziggly
```
Create a python virtual environment and install dependencies
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create an .env file and fill the required environment variables
```
FLASK_APP=app.py
FLASK_ENV=development
CONFIG_TYPE=config.ProductionConfig
BIND_ADDRESS=
ADMIN_USERNAME=
ADMIN_PASSWORD=
```
Start application
```sh
gunicorn -c gunicorn.conf.py
```

## Notable Features
- Inventory Management
- Login System
- Cashier Mode