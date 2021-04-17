#!/usr/bin/env python3

'''
This script downloads TACO's images from Flickr given an annotation json file
Code written by Pedro F. Proenza, 2019
'''

import time
from concurrent.futures import ThreadPoolExecutor
import os.path
import argparse
import json
from PIL import Image
import requests
from io import BytesIO
import sys

parser = argparse.ArgumentParser(description='')
parser.add_argument('--dataset_path', required=False, default='./data/annotations.json', help='Path to annotations')
parser.add_argument('--workers', required=False, default=5, help='The number of workers to use when downloading annotated files.')
args = parser.parse_args()

dataset_dir = os.path.dirname(args.dataset_path)

print('Note. If for any reason the connection is broken. Just call me again and I will start where I left.')

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

        i+=1

    def abort_on_exception(fut):
        if fut is not None and fut.done() and fut.exception():
            sys.exit(1)

    def wait_for(futures):
      noned = [f for f in futures if f is None]
      some = [f for f in futures if f is not None]

      running = [f for f in some if not f.done()]
      done = [f for f in some if f.done()]
      failed = [f for f in done if f.exception()]

      print("none", len(noned), "some", len(some), "running", len(running), "done", len(done), "failed", len(failed))

      if any(failed):
        sys.exit(1)

      return running


    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(download, i) for i in range(nr_images)]

        running = futures

        while True:
            try:
                running = wait_for(running)

                if len(running) < 1:
                  sys.exit()

                #futures = [f for f in futures if not f.done()]

                #bar_size = 30
                #i = nr_images - len(futures)
                #x = int(bar_size * i / nr_images)
                #fmt = "\033[KLoading: [{}{}] - {}/{} ({} workers)\r"
                #sys.stdout.write(fmt.format("=" * x, "." * (bar_size - x), i, nr_images, args.workers))
                #sys.stdout.flush()

                time.sleep(0.25)
            except BaseException as err:
              print("Fuck exceptions")
              executor.shutdown(wait=False, cancel_futures=False)

    sys.stdout.write('Finished\n')
