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
tuple_holder = []
tree = getTree(username)
for i in tree.xpath("//div[@id='common_question_container']/div"):
    #question
    for j in i.xpath("div/span/span"):
        question = (" ".join(j.text.split('\n')))
    #asked_by_who
    asked_by = i.find('div/span/a')
    if(asked_by == None):
        asked_by_who = "Anonymous"
    else:
        asked_by_who = "@" + (asked_by.get('href').lstrip('/'))
    #answer
    for j in i.xpath("div[3]"):
        answer = (' '.join(j.itertext()).strip())
    #img_reply_bool
    for j in i.xpath("div[3]"):
        nodes = j.getchildren()
        img_reply = False
        for k in nodes:
            if(k.tag == 'a'):
                img_reply = True
        img_reply_bool = (img_reply)
    #img_reply_src
    for j in i.xpath("div[3]"):
        nodes = j.getchildren()
        img_reply_src = (None)
        for k in nodes:
            if(k.tag == 'a'):
                imgTree = html.fromstring(requests.get("http://ask.fm" + k.get('href')).text)
                img_reply_src = (imgTree.xpath("//img[@id='nopup-picture']")[0].get('src'))
    #like_url
    like_url = (None)
    for j in i.xpath("div[5]/div[2]/a"):
        like_url = ("http://ask.fm" + j.get("href"))
    #like_count
    for j in i.xpath("div[5]/div[2]"):
        nodes = j.getchildren()
        if(len(nodes) == 0):
            like_count = (None)
        else:
            like_count = (nodes[0].text.split(' ')[0])
    tuple_holder.append((question, asked_by_who, answer, img_reply_bool, img_reply_src, like_url, like_count))

for i in tuple_holder:
    print("Question: " + i[0])
    print("Asked By: " + i[1])
    print("Answer: " + i[2])
    print("Is Image Reply?: " + str(i[3]))
    print("Image Source: " + str(i[4]))
    print("Like URL: " + str(i[5]))
    print("Like Count: " + str(i[6]))
