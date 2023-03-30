#!/usr/bin/env python
from datetime import datetime
import mongoutils
import csv
import sys
import logging
import logging.handlers


def init_logger(name, fname, level):
    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.handlers.RotatingFileHandler(fname, maxBytes=10*1024*2024*1024, backupCount=5)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    return logger


def load_regions(filepath):
    '''
      Load regions from csv
      Format: region;lowleft_lon;lowleft_lat;rightup_lon; rightup_lat

      Output: regions list
    '''
    regions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            # convert lat lon data to float
            float_row = [row[0]]
            for k in row[1:]:
                float_row.append(float(k))
            regions.append(float_row)
    return regions


def get_outfilename(folder, region_name, timerange):
    '''
      Generate output file path with folder + region name + timeranges
    '''
    interval_start_str = timerange[0].strftime('%Y%m%d%H%M%S')
    interval_end_str = timerange[1].strftime('%Y%m%d%H%M%S')
    return f'{folder}/box_{region_name}_{interval_start_str}_{interval_end_str}.json'


if __name__ == "__main__":
    csv_fname = None
    if len(sys.argv) == 2:
        csv_fname = sys.argv[1]
    else:
        print('Usage: ./this_script.py regions_file')
        sys.exit()

    logger = init_logger('extract', 'logs/tweets_by_region_interval.log', logging.INFO)

    logger.info('**************************************************************************')
    logger.info('******************************* STARTING *********************************')
    logger.info('**************************************************************************')

    # time range
    interval = [datetime(2015, 1, 1, 0, 0, 0), datetime(2023, 1, 1, 0, 0, 0)]
    logger.info(f"interval to extract: {interval}")

    # load regions
    regions = load_regions(csv_fname)
    logger.info(f"regions to extract: {regions}")

    # databases names
    dbnames = [f'twitter_{y}' for y in range(interval[0].year, interval[1].year+1)]

    # for each database (minimize connections)
    # extract data from all collections
    for dbname in dbnames:
        logging.info(f'* STARTING {dbname}')
        connection = None
        try:
            connection = mongoutils.startConnection(dbname)
            db = connection[dbname]
            for region in regions:
                logger.info(f'** Starting {region}')
                fpath = get_outfilename('data', region[0], interval)
                try:
                    colls = db.list_collection_names()
                    for colname in colls:
                        if 'system' in colname:
                            continue
                        mongoutils.extract_region_interval(db[colname], region, interval, fpath)
                except Exception as e:
                    logging.error(e)
                    logging.error(f'Error extracting {region} from {db}')
                logger.info(f'** {region} finished.')
        except Exception as e:
            logger.error(e)
        finally:
            if connection:
                connection.close()
        logging.info('* FINISHED {dbname}'.format(dbname=dbname))

    logger.info('**************** FINISHED ****************')
