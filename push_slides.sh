#!/bin/bash

# Check if assets/slides directory exists
if [ ! -d "assets/slides" ]; then
    echo "Error: assets/slides directory not found!"
    echo "Please create the directory and add your slide files first."
    exit 1
fi

echo "🔍 Scanning assets/slides directory..."

# Create the manifest.json file
manifest_file="assets/slides/manifest.json"

# Start the JSON array
echo "[" > "$manifest_file"

# Find all slide files and add them to manifest
first_file=true
for file in assets/slides/*.{pptx,ppt,pdf}; do
    # Check if file actually exists (in case no files match the pattern)
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        
        # Add comma if not the first file
        if [ "$first_file" = true ]; then
            first_file=false
        else
            echo "," >> "$manifest_file"
        fi
        
        # Add filename to manifest (with proper JSON formatting)
        echo -n "  \"$filename\"" >> "$manifest_file"
        echo "📄 Found: $filename"
    fi
done

# Close the JSON array
echo "" >> "$manifest_file"
echo "]" >> "$manifest_file"

# Count slides found
slide_count=$(find assets/slides -name "*.pptx" -o -name "*.ppt" -o -name "*.pdf" | wc -l)
echo "✅ Generated manifest.json with $slide_count slide files"

# Show the contents of the manifest
echo ""
echo "📋 Manifest contents:"
cat "$manifest_file"

# Git operations
echo ""
echo "🚀 Pushing to GitHub..."

# Add all changes
git add .

# Commit with timestamp
commit_message="Update slides and manifest - $(date '+%Y-%m-%d %H:%M')"
git commit -m "$commit_message"

# Push to main branch
git push origin main

echo "✅ Successfully pushed to main branch!"
echo "🌐 Your slides should be available at your GitHub Pages site shortly."
