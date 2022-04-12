# bridges-server-data-reddit
Server to get and store reddit data for student use with BRIDGES.
The server automatically gets a snapshot of the top 50 recommended subreddits at 0, 8, and 16 (midnight, 8am and 4pm).

## Making Requests
### Requesting a Specifc Subreddit and Time
To get a specific subreddit and time use the following URL format
```
http://192.168.2.14:9999/cache?subreddit=news&time_request=1649720965
```
The route you should use is /cache

The parameters to pass are:
  * subreddit : The subreddit you want returned
  * time_request : (OPTIONAL) A UNIX time stamp used to find the closest cached snapshot of the subreddit requested. (Default: most current)


The returned data is in json format such as:
```json
{
"t8tkkx": {
        "id": "t8tkkx",
        "title": "How did y'all started learning programming to the point where you are now?(Story time)",
        "author": "NotEnoughBOOST-_-",
        "score": 10,
        "vote_ratio": 0.92,
        "comment_count": 21,
        "subreddit": "learnprogramming",
        "post_time": 1646671850.0,
        "url": "https://www.reddit.com/r/learnprogramming/comments/t8tkkx/how_did_yall_started_learning_programming_to_the/",
        "text": "So I thought I would ask different people about ... getting into a good job etc. It would be re"
    },
    "t837bf": {
        "id": "t837bf",
        "title": "What does a day in the life of a junior dev look like?",
        "author": "Ssacrificial",
        "score": 784,
        "vote_ratio": 0.97,
        "comment_count": 81,
        "subreddit": "learnprogramming",
        "post_time": 1646586419.0,
        "url": "https://www.reddit.com/r/learnprogramming/comments/t837bf/what_does_a_day_in_the_life_of_a_junior_dev_look/",
        "text": "Hello beautiful ... my job."
    },
    ...
}
```
### Requesting a list of avalible subreddits
Go here to this URL to get a list of the avalible subreddit snapshots we have cached locally.
```http://192.168.2.14:9999/list```



## Running the server locally
Make sure to have all the dependices installed from the requirements file

### Linux

#### Running it

```
export FLASK_APP=run.py
flask run  --host=0.0.0.0 --port=9999
```

### Windows

#### Running it

```
set FLASK_APP=run.py
flask run  --host=0.0.0.0 --port=9999
```
or
```
set FLASK_APP=run.py
python -m flask run --host=0.0.0.0 --port=9999
```
*The commands for windows may need the python value before them depending on how Windows has python pathed


### OS/X

#### Running it

```
export FLASK_APP=run.py
python -m flask run --host=0.0.0.0 --port=9999
```

## Command Line Interface
### Reset local reddit cache
```
flask clear
```

### Force the scheduled Update
```
flask update
```
