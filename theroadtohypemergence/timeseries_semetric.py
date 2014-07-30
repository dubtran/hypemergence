import logging
import csv
import sys

from datetime import datetime
from argparse import ArgumentParser

from semetric.apiclient import SemetricAPI
from semetric.apiclient.entity.artist import Artist

log = logging.getLogger(__name__)

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--apikey', type=str, help='your semetric api key')
    parser.add_argument('--no-header', action="store_true", help='disable the header for the csv file')
    parser.add_argument('--unix-timestamp', action="store_true", help='leave the timestamps as unix epoch time', default=False)
    parser.add_argument('--country', type=str, help='country iso code for the time series')
    parser.add_argument('--variant', type=str, help='variant for the timeseries [default=diff]')
    parser.add_argument('--processing', type=str, help='processing level for the timeseries [default=processed]')
    parser.add_argument('--granularity', type=str, help='granularity for the timeseries [default=day]')
    parser.add_argument('artist_id', type=str, help='name of the artist to find')
    parser.add_argument('dataset', type=str, help='dataset to get the data for')
    args = parser.parse_args()

    if args.apikey is None:
        parser.error("an API key must be provided")

    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(message)s')

    api = SemetricAPI('8db8b6311dc44f6ea32b0331f9cf8b5f')

    log.debug("Loading artist with ID: {0}".format(args.artist_id))

    artist = api.get(Artist, id=u'e6ee861435b24f67a6283e00bf820bab' )

    csvout = csv.writer(sys.stdout, delimiter='\t')
    if not args.no_header:
        csvout.writerow(["timestamp", "value"])

    for ts, value in artist.timeseries(args.dataset, variant=args.variant, processing=args.processing, country=args.country, granularity=args.granularity):
        if args.unix_timestamp:
            timestamp = ts
        else:
            dt = datetime.utcfromtimestamp(ts)
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        csvout.writerow([timestamp, value])