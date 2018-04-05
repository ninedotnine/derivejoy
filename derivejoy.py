#!/usr/bin/python3

import requests
from datetime import datetime, timedelta
from time import sleep
from random import randint

from credentials import *

useragent = "derivejoy version 0.4"
welcome_msg = "DERIVE JOY FROM THIS WEBSITE, I AM A HUMAN"
cachefile = "/home/dan/.cache/derivejoy.log"

min_score_threshold = 2000
badwords = ["eddit", "PsBattle"]

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
    for word in badwords:
        if word in message:
            print(f"not posting, badword {word}")
            return
    data = {"access_token" : access_token, "message" : message}
    r = requests.post(facebook_url, data = data)
    print("posted to facebook:", r.status_code)

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
            sleeptime = randint(7200, 50400) # every 8 hours on average
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
        if score is not None and score > min_score_threshold:
            print("{title}\n{score} (+{ups}, -{downs}) by {author} [{id}]"
                    .format(**data))
            if not seen_before(data):
                backup_post(data)
                post_status(data.get("title"))
                break

if __name__ == "__main__":
    main()
