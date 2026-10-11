'''Export WARC, WET, or WAT record metadata to CSV or JSON.'''

import argparse
import contextlib
import csv
import json
import sys

import fsspec
from warcio.archiveiterator import ArchiveIterator

FIELDS = ('warc_type', 'target_uri', 'date', 'content_type', 'content_length', 'http_status')


def read_records(path):
    with fsspec.open(path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            headers = record.rec_headers
            yield {
                'warc_type': record.rec_type,
                'target_uri': headers.get_header('WARC-Target-URI'),
                'date': headers.get_header('WARC-Date'),
                'content_type': headers.get_header('Content-Type'),
                'content_length': int(headers.get_header('Content-Length')),
                'http_status': int(record.http_headers.get_statuscode()) if record.rec_type == 'response' else None,
            }


def write_csv(records, out):
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(records)


def write_json(records, out):
    json.dump(list(records), out, indent=2)
    out.write('\n')


WRITERS = {'csv': write_csv, 'json': write_json}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='local path or URL (https://, s3://) of a WARC, WET, or WAT file')
    parser.add_argument('-f', '--format', choices=WRITERS, default='csv')
    parser.add_argument('-o', '--output', help='output file (default: stdout)')
    args = parser.parse_args()

    out = open(args.output, 'w', newline='', encoding='utf-8') if args.output else contextlib.nullcontext(sys.stdout)
    with out as stream:
        WRITERS[args.format](read_records(args.input), stream)


if __name__ == '__main__':
    main()
