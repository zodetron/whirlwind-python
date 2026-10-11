# Exporter

Exports record metadata from a WARC, WET, or WAT file to CSV or JSON.

## Usage

```
python exporter/export_records.py <input> [-f csv|json] [-o output]
```

- `input`: local path or remote URL (`https://`, `s3://`)
- `-f`: output format, `csv` (default) or `json`
- `-o`: output file, stdout if omitted

Example:

```
python exporter/export_records.py whirlwind.warc.gz -f json -o records.json
```

Or export all local files into `exporter/output/`:

```
make export
```

## Fields

| Field | Source |
|---|---|
| `warc_type` | `WARC-Type` |
| `target_uri` | `WARC-Target-URI` |
| `date` | `WARC-Date` |
| `content_type` | `Content-Type` |
| `content_length` | `Content-Length` |
| `http_status` | HTTP status code (response records only) |
