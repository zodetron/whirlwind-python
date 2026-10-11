# Changes

## Record metadata export

Added `exporter/export_records.py`, which exports record metadata to CSV or JSON.

- Reads WARC, WET, or WAT files, local or remote, using `fsspec` and `warcio`, the same way `warcio-iterator.py` does.
- Extracts one row per record: type, URI, date, content type, length, and HTTP status.
- Reads records one at a time with a generator and keeps only their headers, so page content is never loaded into memory.
- Writes with `csv.DictWriter` or `json.dump`, chosen by `-f`.
- Uses only the standard library and packages already in `requirements.txt`.

Other changes:

- `Makefile`: added `make export`, which writes the outputs to `exporter/output/`.
- `.gitignore`: ignores `exporter/output/`.
- `exporter/README.md`: usage and field reference.
