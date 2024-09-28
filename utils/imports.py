from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import time
from .helpers import *
from pymongo import MongoClient
from .db import insert_into_db
