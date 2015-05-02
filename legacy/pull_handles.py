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
username = str(sys.argv[1])
tree = getTree(username)

#BROKEN, FIX PENDING.
"""
likes_urls = get_like_urls(tree, username)
usernames = getUsernames(likes_urls)
x = open("list.txt","a")
for i in usernames:
    x.write(i + "\n")
print("Wrote " + str(len(usernames)) + " usernames")
x.close()
"""
