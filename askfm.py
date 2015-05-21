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

def isUserDeactivated(tree):
    try:
        return tree.xpath("//*[@id='kitten-image']/img")[0].get('src') == "/images/kittens/disabled.png"
    except IndexError:
        pass

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
    bio_list = tree.xpath("//*[@id='profile-bio']/div[1]/span")
    if(len(bio_list) > 0):
        return bio_list[0].text

def getWeb(tree):
    web_list = tree.xpath("//*[@id='profile-bio']/div[2]/a")
    if(len(web_list) > 0):
        return web_list[0].text

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
    question_text = (None)
    question_list = question.xpath("div/span")
    for i in question_list:
        for j in i.getchildren():
            if(j.tag == 'span'):
                text = j.text_content()
                if text is not None and text != '':
                    question_text = text.replace('\n', ' ').replace('\r', ' ')
    #asked_by_who
    asked_by = question.find('div/span/a')
    if(asked_by == None):
        asked_by_who = "Anonymous"
    else:
        asked_by_who = "@" + ((asked_by.get('href').lstrip('/')).encode('ascii', 'ignore').decode())
    #answer
    answer = (None)
    for j in question.xpath("div[3]"):
        answer = ((' '.join(j.itertext()).strip()).encode('ascii', 'ignore').decode())
    #img_reply_bool
    img_reply_bool = (None)
    for j in question.xpath("div[3]"):
        nodes = j.xpath("a/span")
        img_reply = False
        if(len(nodes) > 0):
            for k in nodes[0]:
                if(k.tag == 'img'):
                    img_reply = True
        img_reply_bool = (img_reply)
    #img_reply_src
    img_reply_src = (None)
    for j in question.xpath("div[3]"):
        if(img_reply_bool == False):
            img_reply_src = (None)
        else:
            nodes = j.getchildren()
            for k in nodes:
                if(k.tag == 'a'):
                    if(len(k.getchildren()) > 0):
                        imgTree = html.fromstring(requests.get("http://ask.fm" + k.get('href')).text)
                        img_reply_src = (imgTree.xpath("//img[@id='nopup-picture']")[0].get('src'))
    #like_url
    like_url = (None)
    for j in question.xpath("div[5]/div[2]/a"):
        like_url = ("http://ask.fm" + j.get("href"))
    #like_count
    like_count = (None)
    for j in question.xpath("div[5]/div[2]"):
        nodes = j.getchildren()
        if(len(nodes) != 0):
            like_count = (nodes[0].text.split(' ')[0])
    #like_list
    like_list = (None)
    if(like_url != None):
        like_list = getUsernames(like_url)

    #answer_id
    answer_id = (None)
    match = re.match('question_box_(\d{12})', question.get('id'))
    if match is not None:
        answer_id = match.group(1)

    return_data = {
        "answer_id":answer_id,
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

def getAnswers(username, delay):
    dict_holder = []
    tree = getTree(username)
    for i in tree.xpath("//div[@class='questionBox']"):
        dict_holder.append(responseSorter(i))

    if(len(tree.xpath("//*[@id='more-container']")) == 0):
        return dict_holder

    next_page = -1
    while(True):
        if delay > 0:
            sleep(delay)

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

def getUser(username, delay=0):
    tree = getTree(username)
    if(isUserDeactivated(tree)):
        return None
    else:
        user = {}
        user["username"] = username
        user["fullname"] = getFullname(tree)
        user["dp"] = getDP(tree)
        user["bio"] = getBio(tree)
        user["web"] = getWeb(tree)
        user["user_answer_count"] = getAnswerCount(tree)
        user["user_like_count"] = getLikeCount(tree)
        user["user_gift_count"] = getGifts(tree)
        user["answers"] = getAnswers(username, delay)
        return user
