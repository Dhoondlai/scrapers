from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import time
from helpers import *
from db import insert_to_dynamodb, mark_vendor_products_inactive
