#!/usr/bin/python3

import requests
from datetime import datetime, timedelta
from time import sleep
from random import randint

from credentials import *

useragent = "derivejoy version 0.5"
welcome_msg = "DERIVE JOY FROM THIS WEBSITE, I AM A HUMAN"
cachefile = "/home/dan/.cache/derivejoy.log"

min_score_threshold = 2000
badwords = ["eddit", "PsBattle", "pvote"]

reddit_url = "https://www.reddit.com/r/subredditsimulator/top/.json?t=today&limit=5"
facebook_url = "https://graph.facebook.com/v2.11/me/feed"

def load_posts(url):
    response = requests.get(url, headers = {"User-Agent" : useragent})
    if response.status_code != 200:
        return None
    return response.json().get("data", {}).get("children")

def seen_before(postdata):
    try:
        logfile = open(cachefile, mode='r')
        for line in logfile:
            postID = line.split(']')[0].split('[')[1]
            if postID == postdata.get("id"):
                print("found a match. i've seen this one before.")
                return True
        return False
    except OSError:
        return False # the log must be empty!

def post_status(message):
    data = {"access_token" : access_token, "message" : message}
    response = requests.post(facebook_url, data = data)
    if response.status_code == 400:
        print("code 400. maybe your user access token is expired?")
    else:
        print("posted to facebook:", response.status_code)

def backup_post(postdata):
    # logfile has format: timestamp [id] title (score (ups, downs)) by author
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(cachefile, mode='a') as log:
        log.write(currentTime)
        log.write(" [{id}] {title} ({score} (+{ups}, -{downs})) by {author}\n"
                .format(**postdata))

def first_run():
    post_status(welcome_msg)
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(cachefile, mode='x') as log:
            log.write(currentTime)
            log.write(" [!<|°_°|>!] ")
            log.write(welcome_msg)
            log.write('\n')
    except:
        raise
    print("initialized!")

def clean_message(message):
    # what to do for "PsBattle" ?
    if "eddit" in message:
        message = message.replace("reddit", "facebook")
        message = message.replace("Reddit", "Facebook")
    if "pvote" in message:
        message = message.replace("upvote", "like")
        message = message.replace("Upvote", "Like")
    print("cleaned message: ", message)
    for word in badwords:
        if word in message:
            print(f"not posting, badword {word}")
            return None
    print("cleaned message: ", message)
    return message

def main():
    try:
        with open(cachefile, mode='r') as log:
            print("log file loaded.")
    except FileNotFoundError:
        first_run()
        exit(0)

    while True:
        try:
            mainloop()
            sleeptime = randint(36000, 72000) # every 15 hours on average
            wakey = timedelta(seconds=sleeptime) + datetime.now()
            print(f"next check at {wakey.strftime('%Y-%m-%d %H:%M:%S')}")
            sleep(sleeptime)
        except KeyboardInterrupt:
            print("interrupt received, quitting.")
            exit(0)

def mainloop():
    posts = load_posts(reddit_url);
    if posts == None:
        print("ERROR: no post found!")
        return
    print("---------------------------------------------------")
    for post in posts:
        data = post.get("data")
        if data == None:
            print("why no data?")
            continue
        if data.get("stickied"):
            continue
        assert post['kind'] == "t3"
        score = data.get("score")
        if score is None or score < min_score_threshold:
            continue
        print("{title}\n{score} (+{ups}, -{downs}) by {author} [{id}]"
                .format(**data))
        if not seen_before(data):
            message = clean_message(data.get("title"))
            if message is None:
                continue
            backup_post(data)
            post_status(message)
            break

if __name__ == "__main__":
    main()
