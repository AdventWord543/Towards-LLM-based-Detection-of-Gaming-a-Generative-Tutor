#!/bin/bash

# Claude Code Auto-Loop Script
# Runs a classification task repeatedly until no files remain in Check folder
# Usage: bash claude_loop.sh [max_iterations]

PROMPT='Read Outer Loop.txt for instructions on how to analyse. Pick a random text file from the Check1 folder to analyse. Add your result to classifications.csv (do not read that csv before finishing your analysis). Seperately, add (echo) the logical steps of your reasoning for the classification to outer_loop_reasoning.csv, be sure to mention the relevant filename at the start. Then move to the file to the checked folder, use the mv command to do this, not move. All slashes in the filepath should be / to function correctly. When you are finished, end your report with the phrase CLASSIFICATION FINISHED.'

TRIGGER="CLASSIFICATION FINISHED"
WORKDIR="C:/Users/Sebas/Desktop/BrainBoost/Classification"
MAX_ITERATIONS=${1:-0}  # Default 0 means unlimited

cd "$WORKDIR"

echo "=== Claude Code Loop Script ==="
echo "Trigger phrase: $TRIGGER"
echo "Working directory: $WORKDIR"
if [ "$MAX_ITERATIONS" -gt 0 ]; then
    echo "Max iterations: $MAX_ITERATIONS"
else
    echo "Max iterations: unlimited"
fi
echo "Press Ctrl+C to stop"
echo ""

iteration=1

while true; do
    # Check if we've reached max iterations
    if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$iteration" -gt "$MAX_ITERATIONS" ]; then
        echo "=== Reached max iterations ($MAX_ITERATIONS). Done! ==="
        break
    fi
    # Check if there are files left in Check1 folder
    file_count=$(ls -1 Check1 2>/dev/null | wc -l)
    files_list=$(ls -1 Check1 2>/dev/null | head -5)

    if [ "$file_count" -eq 0 ]; then
        end_time=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$end_time] === No more files in Check1 folder. Done! ==="
        break
    fi

    start_time=$(date "+%Y-%m-%d %H:%M:%S")
    echo "========================================"
    echo "[$start_time] ITERATION $iteration"
    echo "========================================"
    echo "Files remaining: $file_count"
    echo "Next files in queue:"
    echo "$files_list"
    echo "----------------------------------------"
    echo ""

    # Run Claude Code and capture output
    # The -p flag runs non-interactively and prints the response
    output=$(claude -p --model claude-opus-4-5-20251101 --max-turns 50 "$PROMPT" 2>&1)

    # Show full output
    echo "--- FULL CLAUDE RESPONSE ---"
    echo "$output"
    echo "--- END RESPONSE ---"
    echo ""

    end_time=$(date "+%Y-%m-%d %H:%M:%S")

    # Check if trigger phrase was found
    if echo "$output" | grep -q "$TRIGGER"; then
        echo "[$end_time] === Trigger detected! Starting next iteration... ==="
        echo ""
        iteration=$((iteration + 1))
        sleep 2
    else
        echo "[$end_time] === Trigger not found. Stopping. ==="
        break
    fi
done

echo "=== Script finished after $((iteration - 1)) iteration(s) ==="
