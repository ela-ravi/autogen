#!/bin/bash
# Cleanup script - removes redundant files from root directory

echo "🧹 Cleaning up root directory..."
echo "Keeping only: .env, .gitignore, README.md, transcribe_video/"
echo ""

# Array of files/folders to delete
FILES_TO_DELETE=(
    "continue_workflow.py"
    "post_process_recap.py"
    "run_complete_workflow.py"
    "run_recap_workflow.py"
    "test_modular_workflow.py"
    "reorganize.py"
    "update_file_paths.py"
    "QUICK_REFERENCE.md"
    "REORGANIZATION_PLAN.md"
    "docs"
)

# Confirm with user
echo "The following will be deleted:"
for item in "${FILES_TO_DELETE[@]}"; do
    if [ -e "$item" ]; then
        echo "  - $item"
    fi
done
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

echo ""
echo "Deleting files..."

# Delete each item
for item in "${FILES_TO_DELETE[@]}"; do
    if [ -e "$item" ]; then
        rm -rf "$item"
        echo "✅ Deleted: $item"
    fi
done

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "Root directory now contains:"
ls -la | grep -v "^\." | tail -n +2
echo ""
echo "✅ transcribe_video module is self-contained and ready to use!"

