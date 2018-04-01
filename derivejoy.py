#!/usr/bin/python3

import requests
import urllib.request
import json
from datetime import datetime, timedelta
from time import sleep
from random import randint

from credentials import *

useragent = "derivejoy version 0.4"
welcome_msg = "DERIVE JOY FROM THIS WEBSITE, I AM A HUMAN"
cachefile = "/home/dan/.cache/derivejoy.log"

min_score_threshold = 2000
reddit_url = "https://www.reddit.com/r/subredditsimulator/top/.json?t=today&limit=5"
facebook_url = "https://graph.facebook.com/v2.11/me/feed"

def load_posts(url):
    req = urllib.request.Request(url)
    req.add_header("User-agent", useragent)
    with urllib.request.urlopen(req) as httpresponse:
        if httpresponse.getcode() != 200:
            return None
        loaded = json.load(httpresponse)
    return loaded['data']['children']

def seen_before(post):
    try:
        logfile = open(cachefile, mode='r')
        for line in logfile:
            postID = line.split(']')[0].split('[')[1]
            if postID == post['data']['id']:
                print("found a match. i've seen this one before.")
                return True
        return False
    except OSError:
        return False # the log must be empty!

def post_status(message):
    r = requests.post(facebook_url, data =
                        {"access_token" : access_token, "message" : message})
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
        mainloop()
        sleeptime = randint(7200, 50400) # every 8 hours on average
        wakey = timedelta(seconds=sleeptime) + datetime.now()
        print(f"next check at {wakey.strftime('%Y-%m-%d %H:%M:%S')}")
        sleep(sleeptime)

def mainloop():
    posts = load_posts(reddit_url);
    if posts == None:
        print("ERROR: no post found!")
        return
    print("---------------------------------------------------")
    for post in posts:
        if post['data']['stickied']:
            continue
        assert post['kind'] == "t3"
        if int(post['data']['score']) > min_score_threshold:
            print("{title}\n{score} (+{ups}, -{downs}) by {author} [{id}]"
                    .format(**post['data']))
            if not seen_before(post):
                backup_post(post['data'])
                post_status(post['data']['title'])
                break

if __name__ == "__main__":
    main()
