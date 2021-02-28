#!/bin/sh -l
set -e

CONTENT="$1"
CONTENT_64="$2"
CONTENT_URL="$3"
ZIP_64="$4"

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
INPUT_MARKDOWN="markdown.md"

if [ -n "$CONTENT" ]; then
  echo "$CONTENT" > "$INPUT_MARKDOWN"
elif [ -n "$CONTENT_64" ]; then
  echo "$CONTENT_64" | base64 -d > "$INPUT_MARKDOWN"
elif [ -n "$CONTENT_URL" ]; then
  curl "$CONTENT_URL" -o "$INPUT_MARKDOWN"
elif [ -n "$ZIP_64" ]; then
  echo "$ZIP_64" | base64 --decode > input.zip
  unzip input.zip
  
  FILES=( $(ls *.md) )
  
  if [ "${#FILES[@]}" != 1 ]; then
    echo "expected a single markdown file in the zip archive"
    exit 1
  fi
  
  INPUT_MARKDOWN="${FILES[0]}"
else
  echo "either content, encoded content, or content URL must be provided"
  echo "usage: (content) (content base 64) (content URL)"
  exit 2
fi

python3 /app/run.py "$INPUT_MARKDOWN" output.pdf
echo "::set-output name=pdf_data::$(base64 -w0 output.pdf)"