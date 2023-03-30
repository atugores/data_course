#!/usr/bin/env python
from pymongo import MongoClient
from os.path import expanduser
import configparser
import json
import logging


# create logger
module_logger = logging.getLogger('extract.auxiliary')


def startConnection(database_name, h=None):
    # get configuration data to open connection
    home = expanduser("~")
    config = configparser.RawConfigParser(allow_no_value=True)
    with open(home + "/.crawling.cfg") as ifh:
        config.readfp(ifh)

    if not h:
        h = config.get("mongoclient", "host")

    dbnamecfg = database_name
    if database_name.startswith('twitter'):
        dbnamecfg = 'twitter'
    port = config.get("mongoclient", "port")
    user = config.get(dbnamecfg, "ruser")
    pwd = config.get(dbnamecfg, "rpwd")

    # connect to DB
    mongoserver_uri = f"mongodb://{user}:{pwd}@{h}:{port}/{database_name}?authSource={database_name}"
    conection = MongoClient(host=mongoserver_uri, replicaset='rs00')
    return conection


def flatten_tweetdata(tweet):
    '''
        Reduce json depth.
    '''
    if not isinstance(tweet["created_at"], str):
        tweet["created_at"] = str(tweet["created_at"].isoformat())
    tweet['uid'] = tweet['user']['id']
    del tweet['user']
    tweet['coords'] = tweet['coordinates']['coordinates']
    del tweet['coordinates']
    return tweet


def extract_region_interval(col, region, timerange, out):
    lons_lats = region[1:]

    module_logger.info(f' Extracting {region[0]} from {col.full_name} for timerange: {timerange}')
    module_logger.info('   and storing to {outfile}'.format(outfile=out))

    # data to retrieve from each tweet
    projection = {'coordinates.coordinates': 1,
                  'created_at': 1,
                  'user.id': 1,
                  '_id': 0}

    num_tweets = 0
    result = None
    with open(out, 'a') as f:
        try:
            module_logger.debug('    start find')
            module_logger.info(f'bbox: lowleft={lons_lats[0:2]} upperright={lons_lats[2:]}')
            result = col.find({'coordinates.coordinates': {'$geoWithin': {'$box': [lons_lats[0:2], lons_lats[2:]]}},
                               'created_at': {"$gt": timerange[0], "$lt": timerange[1]}},
                              projection=projection,
                              no_cursor_timeout=True)
            for tweet in result:
                try:
                    if num_tweets % 100000 == 0:
                        module_logger.info('  extracted {n} tweets'.format(n=num_tweets))
                    num_tweets += 1
                    tweet = flatten_tweetdata(tweet)
                    # tweet["_id"] = str(tweet["_id"])
                    f.write(json.dumps(tweet) + '\n')
                except Exception as inst:
                    module_logger.error('Error parsing tweet:')
                    module_logger.error(inst)
            module_logger.debug('    end find')

            module_logger.info('  numTweets: {n}'.format(n=num_tweets))
        finally:
            if result:
                result.close()
