import sys
import os
import requests
import re
import json
from time import sleep
from lxml import html
from askfm import *

if(len(sys.argv)==0):
    exit(0)

username = sys.argv[1]
dicts = getAnswers(username)
for i in dicts:
    print("Question: " + i["question_text"])
    print("Asked By: " + i["asked_by_who"])
    print("Answer: " + i["answer"])
    print("Is Image Reply?: " + str(i["img_reply_bool"]))
    print("Image Source: " + str(i["img_reply_src"]))
    print("Like URL: " + str(i["like_url"]))
    print("Like Count: " + str(i["like_count"]))
    print("Like List:" + str(i["like_list"]))
