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
}
```
### Requesting a list of avalible subreddits
Go here to this URL to get a list of the avalible subreddit snapshots we have cached locally.
```     ```



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
