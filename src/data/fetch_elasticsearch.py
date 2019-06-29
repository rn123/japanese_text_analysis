#!/usr/bin/env python

import os
import subprocess
import time

import defopt
from elasticsearch import Elasticsearch
from logzero import logger
import requests


PROJECT_DIR = os.path.expandvars('$PWD')
EXTERNAL = os.path.abspath(os.path.join(PROJECT_DIR, "src/external"))



def download(*, dirname: str = EXTERNAL):
    es_url = "https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.3.tar.gz"
    filename = os.path.split(es_url)[-1]
    filename_path = os.path.join(dirname, filename)

    if not os.path.isfile(filename_path):
        logger.info(f"Fetching {es_url}")
        resp = requests.get(es_url)
        with open(filename_path, "wb") as infd:
            infd.write(resp.content)

        logger.info(f"Decompressing {filename_path}")
        subprocess.call(f"cd {dirname} && tar xzfv {filename}", shell=True)
        # TODO: ugh
        bin_dir = os.path.splitext(os.path.splitext(filename_path)[0])[0]
        logger.info(f"You can run elasticsearch with {bin_dir}/bin/elasticsearch")


def run(*, dirname: str = EXTERNAL):

    # Return the full path on disk from path, expanding ~ and environment variables along the way.
    path = os.path.join(dirname, "elasticsearch-6.5.3/bin/elasticsearch")
    bin_path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
    if not os.path.isfile(bin_path):
        logger.warning(f"Elasticsearch binary not found at {bin_path}")
        download(dirname=dirname)

    # Install Elasticserch plugins for ko and zh
    # FIXME don't install these if they're already installed
    plugins = ["analysis-nori", "analysis-smartcn"]
    for plugin in plugins:
        logger.info(f"Installing Elasticsearch plugin {plugin}")
        subprocess.run(f"{bin_path}-plugin install {plugin}", shell=True)

    # start elasticsearch in the background
    subprocess.run(f"{bin_path}", shell=True)


def main():
    print(PROJECT_DIR, EXTERNAL)
    defopt.run([download, run])

if __name__ == "__main__":
    main()
