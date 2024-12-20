#!/bin/bash

# Remove comments from YAML files
find . -name "*.yaml" -o -name "*.yml" | while read file; do
    # Skip if file is empty
    [ -s "$file" ] || continue

    # Remove comment lines and empty lines
    sed -i '' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$file"
done

# Remove comment lines from Chart.yaml specifically
if [ -f Chart.yaml ]; then
    sed -i '' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' Chart.yaml
fi
