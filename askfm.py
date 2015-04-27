import sys
import os
import requests
import re
import json
from time import sleep
from lxml import html

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def getTree(username):
    tree = html.fromstring((requests.get("http://ask.fm/" + username).text).encode('ascii', 'ignore').decode())
    return tree

def getToken(tree):
    return tree.xpath("//*[@id='more-container']")[0].get("onsubmit").split("'")[3]

def getTime(tree):
    return tree.xpath("//*[@id='more-container']")[0][0].get("value")

def getPage(tree):
    return tree.xpath("//*[@id='more-container']")[0][1].get("value")

def getFullname(tree):
    return tree.xpath("//*[@id='profile-name-container']/a/span")[0].text

def getDP(tree):
    return tree.xpath("//*[@id='profile-picture']")[0].attrib["src"]

def getBio(tree):
    return tree.xpath("//*[@id='profile-bio']/div[1]/span")[0].text

def getAnswerCount(tree):
    return tree.xpath("//*[@id='profile_answer_counter']")[0].text

def getLikeCount(tree):
    return tree.xpath("//*[@id='profile_liked_counter']")[0].text

def getGifts(tree):
    return tree.xpath("//*[@id='profile_gifts_counter']")[0].text

def getUsernames(like_url):
    username_list = []
    tree = html.fromstring(requests.get(like_url).text)
    username_list = username_list + extractUsernames(tree)
    pagination = tree.get_element_by_id('page-container', None)
    last_page_of_pagination = 1
    if(pagination != None):
        pages = []
        for i in pagination:
            if(isNumber(i.text)):
                pages.append(int(i.text))
        last_page_of_pagination = (max(pages)+1)
        for a_page in range(2,last_page_of_pagination):
            like_tree = html.fromstring(requests.get(like_url + "?page=" + str(a_page)).text)
            username_list = username_list + extractUsernames(like_tree)
    return username_list

def extractUsernames(like_tree):
    extract_list = []
    for i in like_tree.xpath("//*[@id=\"wrapper\"]/div/div"):
            for j in i.xpath("div/div[2]/span/span"):
                extract_list.append(j.text)
    return extract_list

def responseSorter(question):
    #question_text
    for j in question.xpath("div/span/span"):
        question_text = ((" ".join(j.text.split('\n'))).encode('ascii', 'ignore').decode())
    #asked_by_who
    asked_by = question.find('div/span/a')
    if(asked_by == None):
        asked_by_who = "Anonymous"
    else:
        asked_by_who = "@" + ((asked_by.get('href').lstrip('/')).encode('ascii', 'ignore').decode())
    #answer
    for j in question.xpath("div[3]"):
        answer = ((' '.join(j.itertext()).strip()).encode('ascii', 'ignore').decode())
    #img_reply_bool
    for j in question.xpath("div[3]"):
        nodes = j.getchildren()
        img_reply = False
        for k in nodes:
            if(k.tag == 'a'):
                img_reply = True
        img_reply_bool = (img_reply)
    #img_reply_src
    for j in question.xpath("div[3]"):
        nodes = j.getchildren()
        img_reply_src = (None)
        for k in nodes:
            if(k.tag == 'a'):
                imgTree = html.fromstring(requests.get("http://ask.fm" + k.get('href')).text)
                img_reply_src = (imgTree.xpath("//img[@id='nopup-picture']")[0].get('src'))
    #like_url
    like_url = (None)
    for j in question.xpath("div[5]/div[2]/a"):
        like_url = ("http://ask.fm" + j.get("href"))
    #like_count
    for j in question.xpath("div[5]/div[2]"):
        nodes = j.getchildren()
        if(len(nodes) == 0):
            like_count = (None)
        else:
            like_count = (nodes[0].text.split(' ')[0])
    #like_list
    like_list= (None)
    if(like_url != None):
        like_list = getUsernames(like_url)

    return_data = {
        "question_text":question_text,
        "asked_by_who":asked_by_who,
        "answer":answer,
        "img_reply_bool":img_reply_bool,
        "img_reply_src":img_reply_src,
        "like_url":like_url,
        "like_count":like_count,
        "like_list":like_list
    }
    return return_data

def getAnswers(username):
    dict_holder = []
    tree = getTree(username)
    for i in tree.xpath("//div[@class='questionBox']"):
        dict_holder.append(responseSorter(i))

    if(len(tree.xpath("//*[@id='more-container']")) == 0):
        return dict_holder

    next_page = -1
    while(True):
        token = getToken(tree)
        time = getTime(tree)
        if(next_page < 0):
            page = getPage(tree)
        else:
            page = next_page
        data = {
            "time":time,
            "page":page,
            "authenticity_token":token
        }
        raw_post_result = requests.post("http://ask.fm/" + username + "/more",params=data)
        if(raw_post_result.text == "$(\"#more-container\").hide();"):
            break
        js_post_result = re.search(r'after\("((?:[^"]+|\\")+)"\)', raw_post_result.text)
        tree_next_page = html.fromstring(bytes(js_post_result.group(1), "utf-8").decode("unicode_escape"))
        for i in tree_next_page[1]:
            dict_holder.append(responseSorter(i))
        next_page = int(re.search(r'\d+', re.search(r'val\(\d+\)', raw_post_result.text).group(0)).group(0))
    return dict_holder
