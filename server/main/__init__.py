from re import template
from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

from .views import *