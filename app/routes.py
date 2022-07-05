from cgitb import small
from concurrent.futures import thread
from imp import cache_from_source
#from turtle import pos

from datetime import datetime
from app import app
from flask import request
from flask import abort
import praw
import time
from logging.handlers import RotatingFileHandler
import logging
import json
import os
import shutil
import sys
from apscheduler.schedulers.background import BackgroundScheduler


if os.getenv("REDDIT_CLIENT") is not None:
    client_id_var = os.getenv("REDDIT_CLIENT")
else:
    print("ERROR: No REDDIT_CLIENT environment variable found")
    exit()

if os.getenv("REDDIT_TOKEN") is not None:
    token = os.getenv("REDDIT_TOKEN")
else:
    print("ERROR: No REDDIT_TOKEN environment variable found")
    exit()

if os.getenv("CACHE_TIME") is not None:
    cache_store_time = os.getenv("CACHE_TIME")
else:
    cache_store_time = 14   # This is days, change this
    cache_store_time = cache_store_time * 86400 #seconds in a day


if not os.path.isdir("app/reddit_data"):
    os.mkdir("app/reddit_data")

sub_list = []


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

""" Cache Route
    get:
        summary: returns a cached subreddit snapshot
        description: Searches the local cache for a subreddit and timestamp match to the query
        path: /cache
        parameters:
            subreddit (String): the subreddit you want the snapshot of
            time_request (int): (OPTIONAL) give a UNIX timestamp of when you want the snapshot to be (Defaults to most recent if no value given)
        responses:
            200:
                description: a json string object that contains the subreddit snapshot
"""
@app.route('/cache')
def request_cached_subreddit():
    try:
        subreddit_name = request.args.get("subreddit")
    except:
        abort(400)
    time_request = request.args.get("time_request")
    if time_request != None:
        time_request = int(time_request)
    if time_request == None or time_request < 0:
        time_request = time.time()
    check = cache_lookup(subreddit_name, time_request)
    if check != None:
        #load file and return
        f = open(f"app/reddit_data/{check}")
        data = json.load(f)
        f.close()

        return data
    else:
        abort(400)


@app.route('/hash')
def reddit_hash():
    try:
        subreddit_name = request.args.get("subreddit")
    except:
        abort(400)
    time_request = request.args.get("time_request")
    if time_request == None or time_request < 0:
        time_request = time.time()
    
    fi = cache_lookup(subreddit_name, time_request)
    if fi != None:
        return fi.replace(".json", "")
    return "false"



""" List Route
    get:
        summary: returns a list of cached subreddit snapshot
        description: Generates a HTML string to display the list of avalible reddit snapshots
        path: /list
        parameters:
            None
        responses:
            200:
                description: A HTML string with the avaliable subreddit snapshots
"""
@app.route('/list')
def return_list():
    sub_reddit_list = ""
    for i in sub_list:
        sub_reddit_list = sub_reddit_list + i + "<br>"
    return sub_reddit_list

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


    time_marker = int(time.time()) #time of file generation
    file_name = f"redditdata_{subreddit_name}_{time_marker}"

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


'''
Takes in a subreddit object and parses it out into
our own json format to get ride of useless info
'''
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


    # TWO WEEK CACHING LIMIT, ENVIRONMENT VARIABLE WITH DEAFULT 2 WEEKS
    print("Updating...")
    ar = os.listdir("app/reddit_data")

    #generates the list of default subreddits
    if not sub_list:
        for x in reddit.subreddits.default():
            sub_list.append(x.display_name)
    for i in sub_list:
        request_reddit(i, 1000)
    print("Updated")
    for f in ar:
        file_split = f.split("_")
        file_time = int(file_split[2].replace(".json", ""))
        if (int(time.time()) - file_time) > cache_store_time:
            os.remove(f"app/reddit_data/{f}")



def html_output(data):
    out = ""
    for post in data:
        out = out + f"{data[post]['title']} | {data[post]['author']} | {data[post]['score']}<br>"
    return out

@app.cli.command('update')
def force_update():
    threaded_update()

@app.cli.command('clear')
def clear_cache():
    shutil.rmtree("app/reddit_data")
    os.mkdir("app/reddit_data")

''' 400 Errors
Handles an abort(400) request
This is mainly used for when the subreddit the user requested isnt in the list
or they left that variable blank
'''    
@app.errorhandler(400)
def no_subreddit(e):
    #returns an error string if the subreddit is invalid
    return "400 Error Subreddit not valid", 400


#setting up the server log
format = logging.Formatter('%(asctime)s %(message)s') 

logFile = 'log.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(format)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(level=logging.INFO)

app_log.addHandler(my_handler)




update_sched = BackgroundScheduler()
update_sched.daemonic = True
update_sched.start()

update_sched.add_job(threaded_update, trigger='cron', hour='0,8,16', misfire_grace_time=None, max_instances=1)
update_sched.print_jobs()
