'''Tests for exporter/export_records.py against the sample whirlwind files.'''

import csv
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'exporter'))

from export_records import FIELDS, read_records, write_csv, write_json  # noqa: E402


def records(name):
    return list(read_records(str(ROOT / name)))


class TestReadRecords(unittest.TestCase):
    def test_record_types(self):
        cases = {
            'whirlwind.warc.gz': ['warcinfo', 'request', 'response', 'metadata'],
            'whirlwind.warc.wet.gz': ['warcinfo', 'conversion'],
            'whirlwind.warc.wat.gz': ['warcinfo', 'metadata'],
        }
        for name, types in cases.items():
            with self.subTest(name=name):
                self.assertEqual([r['warc_type'] for r in records(name)], types)

    def test_response_fields(self):
        response = records('whirlwind.warc.gz')[2]
        self.assertEqual(response['target_uri'], 'https://an.wikipedia.org/wiki/Escopete')
        self.assertEqual(response['http_status'], 200)
        self.assertGreater(response['content_length'], 0)

    def test_status_only_on_response(self):
        for record in records('whirlwind.warc.gz'):
            if record['warc_type'] != 'response':
                self.assertIsNone(record['http_status'])


class TestWriters(unittest.TestCase):
    def test_csv(self):
        out = io.StringIO()
        write_csv(records('whirlwind.warc.gz'), out)
        rows = list(csv.DictReader(io.StringIO(out.getvalue())))
        self.assertEqual(len(rows), 4)
        self.assertEqual(tuple(rows[0]), FIELDS)

    def test_json(self):
        out = io.StringIO()
        write_json(records('whirlwind.warc.gz'), out)
        self.assertEqual(json.loads(out.getvalue()), records('whirlwind.warc.gz'))


if __name__ == '__main__':
    unittest.main()
