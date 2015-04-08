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

def get_like_urls(tree, username):
    likes_urls = []
    usernames = []
    
    for i in tree.xpath("//div[@id='common_question_container']/div"):
        for j in i.xpath("div[5]/div[2]/a"):
            print("http://ask.fm" + j.get("href"))
            likes_urls.append("http://ask.fm" + j.get("href"))
            
    if(len(tree.xpath("//*[@id='more-container']")) == 0):
        return likes_urls

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
        page_plus_one = requests.post("http://ask.fm/" + username + "/more",params=data)
        if(page_plus_one.text == "$(\"#more-container\").hide();"):
            break
        reg_html_page_plus_one = re.search(r'after\("((?:[^"]+|\\")+)"\)', page_plus_one.text)
        html_page_plus_one = bytes(reg_html_page_plus_one.group(1), "utf-8").decode("unicode_escape")
        tree_page_plus_one = html.fromstring(html_page_plus_one)
        for i in tree_page_plus_one[1]:
            for j in i.xpath("div[5]/div[2]/a"):
                print("http://ask.fm" + j.get("href"))
                likes_urls.append("http://ask.fm" + j.get("href"))
        next_page = int(re.search(r'\d+', re.search(r'val\(\d+\)', page_plus_one.text).group(0)).group(0))
    
    return likes_urls

def returnUsernames(like_url):
    username_list = []
    print("From answer: " + like_url)
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
            print("Pagination: " + str(a_page) + " of " + str((last_page_of_pagination)-1))
            like_tree = html.fromstring(requests.get(like_url + "?page=" + str(a_page)).text)
            username_list = username_list + extractUsernames(like_tree)
    return username_list

def extractUsernames(like_tree):
    extract_list = []
    for i in like_tree.xpath("//*[@id=\"wrapper\"]/div/div"):
            for j in i.xpath("div/div[2]/span/span"):
                #print("  " + j.text)
                extract_list.append(j.text)
    return extract_list
    
    
def getUsernames(likes_urls):
    usernames = []
    i = 0
    while i < len(likes_urls):
        try:
            print("Getting likes: " + str(i+1) + "  of " + str(len(likes_urls)) + " | " + str(round((((i+1) / (len(likes_urls))) * 100),2))  + " Percentage complete")
            returned_usernames = returnUsernames(likes_urls[i])
            print("Got " + str(len(returned_usernames)) + " usernames")
            usernames = usernames + returned_usernames
            i += 1
        except KeyboardInterrupt:
            exit(0)
        except:
            print("Failed: " + str(i))
            sleep_time = 5
            print("Sleeping for: " + str(sleep_time) + " seconds")
            sleep(sleep_time)
    return set(usernames)
