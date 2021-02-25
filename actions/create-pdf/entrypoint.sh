#!/bin/sh -l
set -e

CONTENT="$1"
CONTENT_64="$2"
CONTENT_URL="$3"

INPUT_MARKDOWN=$(mktemp tmpXXXXXX.md)

if [ -n "$CONTENT" ]; then
  echo "$CONTENT" > "$INPUT_MARKDOWN"
elif [ -n "$CONTENT_64" ]; then
  echo "$CONTENT_64" | base64 -d > "$INPUT_MARKDOWN"
elif [ -n "$CONTENT_URL" ]; then
  curl "$CONTENT_URL" -o "$INPUT_MARKDOWN"
else
  echo "either content, encoded content, or content URL must be provided"
  echo "usage: (content) (content base 64) (content URL)"
  exit 1
fi

OUTPUT_PDF=$(mktemp tmpXXXXXX.pdf)
python3 /app/run.py "$INPUT_MARKDOWN" "$OUTPUT_PDF"

echo "::set-output name=pdf_data::$(base64 -w0 "$OUTPUT_PDF")"