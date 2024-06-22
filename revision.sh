#!/bin/bash

# Ask the user for a message
read -p "Enter the revision message: " message

# Generate a new Alembic revision
alembic revision --autogenerate -m "$message"

# Directory where the Alembic versions are stored
VERSIONS_DIR="alembic/versions"

# Get the count of the existing .py files in the versions directory
file_count=$(ls -1 $VERSIONS_DIR/*.py 2>/dev/null | wc -l)

# Get the latest revision file (assuming it's the most recently modified .py file that doesn't start with {number}_)
latest_revision=$(ls -t $VERSIONS_DIR/*.py 2>/dev/null | grep -vE '/[0-9]+_.*\.py$' | head -1)

# Check if a revision was generated
if [[ -z "$latest_revision" ]]; then
    echo "No new revision file found."
    exit 1
fi

# Extract the filename from the full path
latest_revision_filename=$(basename "$latest_revision")

# Construct the new filename
new_filename="${file_count}_${latest_revision_filename}"

# Rename the generated file
mv "$latest_revision" "$VERSIONS_DIR/$new_filename"

echo "Revision file has been renamed to: $new_filename"
