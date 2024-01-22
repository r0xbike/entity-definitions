#!/usr/bin/env python3

import argparse
import os
from pprint import pprint

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

parser = argparse.ArgumentParser(description='Remove metric queries from Infra golden metrics.')
parser.add_argument('directory', help='top-level entity-types directory containing golden_metrics.yml files')
args = parser.parse_args()

cloud_prefixes = ['aws', 'azure', 'gcp']
gm_filename = 'golden_metrics.yml'


def get_golden_metrics_filepaths(directory, *args):
    gm_filepaths = []

    for dirpath, dirnames, filenames in os.walk(directory, topdown=True):
        dirnames[:] = [d for d in dirnames if d.startswith('infra') and not any(map(d.__contains__, cloud_prefixes))]
        filenames[:] = [f for f in filenames if f == gm_filename]

        for filename in filenames:
            gm_filepaths.append(os.path.join(dirpath, filename))

    return gm_filepaths

def load_golden_metrics_file(filepath):
    with open(filepath, 'r') as f:
        data = load(f, Loader=Loader)

    return data

def write_golden_metrics_file(filepath, file_contents):
    with open(filepath, 'w') as golden_metrics_file:
        print(dump(file_contents, Dumper=Dumper, sort_keys=False), file=golden_metrics_file)

def remove_metrics_queries(filepaths):
    for filepath in filepaths:
        data = load_golden_metrics_file(filepath)
        print(filepath)

        for key in data:
            try:
                x = data[key]['queries']
                y = data[key]['queries']['newRelic']['from']
                z = data[key]['queries']['newRelicSample']
            except KeyError:
                break

            if not data[key]['queries']['newRelic']['from'] == "Metric":
                break

            data[key]['queries'].pop('newRelic')
            data[key]['queries']['newRelic'] = data[key]['queries'].pop('newRelicSample')

        write_golden_metrics_file(filepath, data)


def main():
    golden_metrics_filepaths = get_golden_metrics_filepaths(args.directory)
    remove_metrics_queries(golden_metrics_filepaths)


if __name__ == "__main__":
    main()
