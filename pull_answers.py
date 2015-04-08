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
username = "LokeshPoovaragan"
question_list = []
asked_by_list = []
answer_list = []
img_reply_bool_list = []
img_reply_src_list = []
like_count_list = []
tree = getTree(username)
for i in tree.xpath("//div[@id='common_question_container']/div"):
	for j in i.xpath("div/span/span"):
		question_list.append(" ".join(j.text.split('\n')))
for i in tree.xpath("//div[@id='common_question_container']/div"):
	asked_by = i.find('div/span/a')
	if(asked_by == None):
		asked_by_list.append("Anonymous")
	else:
		asked_by_list.append(asked_by.text)
for i in tree.xpath("//div[@id='common_question_container']/div"):
	for j in i.xpath("div[3]"):
		answer_list.append(' '.join(j.itertext()).strip())
for i in tree.xpath("//div[@id='common_question_container']/div"):
	for j in i.xpath("div[3]"):
		nodes = j.getchildren()
		img_reply = False
		for k in nodes:
			if(k.tag == 'a'):
				img_reply = True
		img_reply_bool_list.append(img_reply)
for i in tree.xpath("//div[@id='common_question_container']/div"):
	for j in i.xpath("div[3]"):
		nodes = j.getchildren()
		for k in nodes:
			if(k.tag == 'a'):
				imgTree = html.fromstring(requests.get("http://ask.fm" + k.get('href')).text)
				img_reply_src_list.append(imgTree.xpath("//img[@id='nopup-picture']")[0].get('src'))
			else:
				img_reply_src_list.append(None)
for i in tree.xpath("//div[@id='common_question_container']/div"):
	for j in i.xpath("div[5]/div[2]"):
		nodes = j.getchildren()
		if(len(nodes) == 0):
			like_count_list.append(None)
		else:
			like_count_list.append(nodes[0].text.split(' ')[0])
for i,j,k,l,m,n in zip(question_list, asked_by_list, answer_list, img_reply_bool_list, img_reply_src_list, like_count_list):
    #print(i + "," + j + "," + k + "," + str(l) + "," + str(m) + "," + str(n))
    print(j + "," + str(l) + "," + str(m))
    

		
