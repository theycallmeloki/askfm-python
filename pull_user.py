import sys
import os
import requests
import re
import json
from time import sleep
from lxml import html
from askfm import *

if(len(sys.argv)==0):
    print("Usage: pull_user.py <username>")
    exit(0)

username = sys.argv[1]
tree = getTree(username)
user = {}
user["username"] = username
user["fullname"] = getFullname(tree)
user["dp"] = getDP(tree)
user["bio"] = getBio(tree)
user["web"] = getWeb(tree)
user["user_answer_count"] = getAnswerCount(tree)
user["user_like_count"] = getLikeCount(tree)
user["user_gift_count"] = getGifts(tree)
user["answers"] = getAnswers(username)

print(json.dumps(user,sort_keys=True))
