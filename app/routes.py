from cgitb import small
from concurrent.futures import thread
from imp import cache_from_source
from turtle import pos
from app import app
from flask import request
import praw
import time
import json
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler


if os.getenv("REDDIT_CLIENT") is not None:
    client_id_var = int(os.getenv("REDDIT_CLIENT"))
else:
    print("ERROR: No REDDIT_CLIENT environment variable found")
    exit()

if os.getenv("REDDIT_TOKEN") is not None:
    token = int(os.getenv("REDDIT_TOKEN"))
else:
    print("ERROR: No REDDIT_TOKEN environment variable found")

    exit()



# recommended subreddits: news, Showerthoughts, technology, movies, worldnews, space, nosleep

@app.route('/')
def defaultroute():
    subreddit_name = request.args.get("subreddit")
    post_num = request.args.get("limit", type=int)
    if subreddit_name == "" or post_num == None:
        return "Error"

    check = old_cache_lookup(subreddit_name)
    if check != None:
        #load file and return
        f = open(f"app/reddit_data/{check}")
        data = json.load(f)
        f.close()

        return html_output(data) 
    
    out = request_reddit(subreddit_name, post_num)

    #only return out when using for bridges
    return f"<html><body>{out}</body></html>"
    #return out


@app.route('/cache')
def request_cached_subreddit():
    subreddit_name = request.args.get("subreddit")
    time_request = request.args.get("time_request")
    check = cache_lookup(subreddit_name, time_request)
    if check != None:
        #load file and return
        f = open(f"app/reddit_data/{check}")
        data = json.load(f)
        f.close()

        return html_output(data)
    else:
        return "Subreddit not valid"


def request_reddit(subreddit_name, post_limit):
    reddit = praw.Reddit(
        client_id=client_id_var,
        client_secret=token,
        user_agent="bridges-test",
    )

    outputdata = {}
    out = ""
    nsfw_count = 0


    for sub in reddit.subreddit(subreddit_name).hot(limit=post_limit):
        if (sub.over_18 == True):
            nsfw_count = nsfw_count + 1
            continue
        #print(f"{sub.title} | {sub.author} | {sub.score}")
        temp_json = generate_sub_json(sub)
        outputdata[f"{sub.id}"] = temp_json
    file_name = f"redditdata_{subreddit_name}_{int(time.time())}"

    with open(f"app/reddit_data/{file_name}.json", "w") as outfile:
        json.dump(outputdata, outfile)

    #print(f"NSFW Posts: {nsfw_count}")
    out = html_output(outputdata)
    return out

def cache_lookup(subreddit_name, time_request=time.time()):
    ar = os.listdir("app/reddit_data")
    smallest_diff = sys.maxsize
    return_file_dir = ""
    
    for f in ar:
        file_split = f.split("_")
        file_time = int(file_split[2].replace(".json", ""))
        if file_split[1] == subreddit_name:
            if smallest_diff > abs(int(time_request) - file_time):
                smallest_diff = abs(int(time_request) - file_time)
                return_file_dir = f
    if smallest_diff != sys.maxsize:
        return return_file_dir
    return None

def old_cache_lookup(subreddit_name):
    ar = os.listdir("app/reddit_data")
    smallest_diff = sys.maxsize
    return_file_dir = ""
    
    for f in ar:
        file_split = f.split("_")
        file_time = int(file_split[2].replace(".json", ""))
        if file_split[1] == subreddit_name and (int(time.time()) - file_time) < 43200:
            if smallest_diff > (int(time.time()) - file_time):
                smallest_diff = int(time.time()) - file_time
                return_file_dir = f
        elif file_split[1] == subreddit_name and (int(time.time()) - file_time) > 43200:
            print("old file")    #ToDo: delete old file after x amount of time
    if smallest_diff != sys.maxsize:
        return return_file_dir
    return None

def generate_sub_json(sub):
    sub_json = {}
    sub_json['id'] = sub.id
    sub_json['title'] = sub.title
    sub_json['author'] = str(sub.author)
    sub_json['score'] = sub.score
    sub_json['vote_ratio'] = sub.upvote_ratio
    sub_json['comment_count'] = sub.num_comments
    sub_json['subreddit'] = str(sub.subreddit)
    sub_json['post_time'] = sub.created_utc
    sub_json['url'] = sub.url
    sub_json['text'] = sub.selftext
    


    return sub_json


def threaded_update():
    reddit = praw.Reddit(
        client_id=client_id_var,
        client_secret=token,
        user_agent="bridges-test",
    )

    #generates the list of default subreddits
    sub_list = []
    for x in reddit.subreddits.default():
        sub_list.append(x.display_name)
    for i in sub_list:
        request_reddit(i, 1000)
    print("Updated")


def html_output(data):
    out = ""
    for post in data:
        out = out + f"{data[post]['title']} | {data[post]['author']} | {data[post]['score']}<br>"
    return out

@app.cli.command('update')
def force_update():
    threaded_update()

update_sched = BackgroundScheduler()
update_sched.daemonic = True
update_sched.start()

update_sched.add_job(threaded_update, trigger='cron', hour='0,8,16', misfire_grace_time=None)
update_sched.print_jobs()