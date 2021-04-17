#!/usr/bin/env python3

'''
This script downloads TACO's images from Flickr given an annotation json file
Code written by Pedro F. Proenza, 2019
'''

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import argparse
import json
import os.path
import requests
import sys
import time
import typing as t

parser = argparse.ArgumentParser(description='')
parser.add_argument('--dataset_path', required=False, default='./data/annotations.json', help='Path to annotations')
parser.add_argument('--workers', required=False, default=5, help='The number of workers to use when downloading annotated files.')
args = parser.parse_args()

dataset_dir = os.path.dirname(args.dataset_path)

print('Note. If for any reason the connection is broken. Just call me again and I will start where I left.')

BAR_WIDTH = 30
ANSI_KILL_LINE = "\033[K"
BAR_FMT = "Loading: [{}] - {}/{} ({} workers)\r"

def print_bar(pos: int, stop: int, workers: int) -> None:
    bar_offset = stop - pos
    x = int(BAR_WIDTH * bar_offset / stop)
    bar = ("=" * x) + ("." * (BAR_WIDTH - x))

    sys.stdout.write(ANSI_KILL_LINE)
    sys.stdout.write(BAR_FMT.format(bar, bar_offset, stop, workers))
    sys.stdout.flush()

# Load annotations
with open(args.dataset_path, 'r') as f:
    annotations = json.loads(f.read())

    nr_images = len(annotations['images'])

    def download(i):

        image = annotations['images'][i]

        file_name = image['file_name']
        url_original = image['flickr_url']
        url_resized = image['flickr_640_url']

        file_path = os.path.join(dataset_dir, file_name)

        # Create subdir if necessary
        subdir = os.path.dirname(file_path)
        if not os.path.isdir(subdir):
            os.mkdir(subdir)

        if not os.path.isfile(file_path):
            # Load and Save Image
            response = requests.get(url_original)
            img = Image.open(BytesIO(response.content))
            if img._getexif():
                img.save(file_path, exif=img.info["exif"])
            else:
                img.save(file_path)

    def abort_on_sigint(fn, *args):
        try:
            fn(*args)
        except KeyboardInterrupt:
            print("aborting in worker")
            sys.exit(1)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
                executor.submit(lambda i: abort_on_sigint(download, i), i)
                for i in range(nr_images)
        ]

        outstanding = futures

        while len(outstanding) > 0 and not any([f.exception() for f in outstanding if f.done()]):
            try:
                outstanding = [f for f in outstanding if not f.done() or f.exception()]

                print_bar(len(outstanding), len(futures), args.workers)

                time.sleep(0.25)
            except BaseException as err:
                print(f"handling {err}:{err.__class__}")
                print("Shutting down workers, this may take a few seconds.")

                for fut in futures:
                    fut.cancel()

                executor.shutdown(wait=False)
                raise err

    print('Finished.')
