'''Export WARC, WET, or WAT record metadata or WET page text to CSV or JSON.'''

import argparse
import contextlib
import csv
import json
import sys

import fsspec
from warcio.archiveiterator import ArchiveIterator

FIELDS = ('warc_type', 'target_uri', 'date', 'content_type', 'content_length', 'http_status')
TEXT_FIELDS = ('url', 'language', 'word_count', 'preview')
PREVIEW_CHARS = 200


def iter_archive(path):
    with fsspec.open(path, 'rb') as stream:
        yield from ArchiveIterator(stream)


def read_records(path):
    for record in iter_archive(path):
        headers = record.rec_headers
        yield {
            'warc_type': record.rec_type,
            'target_uri': headers.get_header('WARC-Target-URI'),
            'date': headers.get_header('WARC-Date'),
            'content_type': headers.get_header('Content-Type'),
            'content_length': int(headers.get_header('Content-Length')),
            'http_status': int(record.http_headers.get_statuscode()) if record.rec_type == 'response' else None,
        }


def read_text(path):
    for record in iter_archive(path):
        if record.rec_type != 'conversion':
            continue
        words = record.content_stream().read().decode('utf-8', errors='replace').split()
        yield {
            'url': record.rec_headers.get_header('WARC-Target-URI'),
            'language': record.rec_headers.get_header('WARC-Identified-Content-Language'),
            'word_count': len(words),
            'preview': ' '.join(words)[:PREVIEW_CHARS],
        }


def write_csv(records, fields, out):
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)


def write_json(records, fields, out):
    json.dump(list(records), out, indent=2, ensure_ascii=False)
    out.write('\n')


MODES = {'records': (read_records, FIELDS), 'text': (read_text, TEXT_FIELDS)}
WRITERS = {'csv': write_csv, 'json': write_json}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='local path or URL (https://, s3://) of a WARC, WET, or WAT file')
    parser.add_argument('-m', '--mode', choices=MODES, default='records', help='records: metadata of every record; text: page text from WET')
    parser.add_argument('-f', '--format', choices=WRITERS, default='csv')
    parser.add_argument('-o', '--output', help='output file (default: stdout)')
    args = parser.parse_args()

    reader, fields = MODES[args.mode]
    out = open(args.output, 'w', newline='', encoding='utf-8') if args.output else contextlib.nullcontext(sys.stdout)
    with out as stream:
        WRITERS[args.format](reader(args.input), fields, stream)


if __name__ == '__main__':
    main()
