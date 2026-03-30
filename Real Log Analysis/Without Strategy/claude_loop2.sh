#!/bin/bash

# Claude Code Auto-Loop Script (Loop 2)
# Runs a classification task repeatedly until no files remain in Check2 folder
# Usage: bash claude_loop2.sh [max_iterations]

PROMPT_TEMPLATE='Read "Outer Loop2.txt" for instructions on how to analyse. Analyse the file Check2/FILE_PLACEHOLDER. Add your result to classifications2.csv (do not read that csv before finishing your analysis). Seperately, add (echo) the logical steps of your reasoning for the classification to outer_loop_reasoning2.csv, be sure to mention the relevant filename at the start. Then move the file to the Checked2 folder, use the mv command to do this, not move. All slashes in the filepath should be / to function correctly. When you are finished, end your report with the phrase CLASSIFICATION FINISHED.'

TRIGGER="CLASSIFICATION FINISHED"
WORKDIR="C:/Users/Sebas/Desktop/BrainBoost/Classification"
MAX_ITERATIONS=${1:-0}  # Default 0 means unlimited
FAILED_LOG="failed_files2.log"

cd "$WORKDIR"

echo "=== Claude Code Loop Script (LOOP 2) ==="
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
    # Check if there are files left in Check2 folder
    file_count=$(ls -1 Check2 2>/dev/null | wc -l)
    current_file=$(ls -1 Check2 2>/dev/null | head -1)

    if [ "$file_count" -eq 0 ]; then
        end_time=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$end_time] === No more files in Check2 folder. Done! ==="
        break
    fi

    # Build prompt with specific file
    PROMPT="${PROMPT_TEMPLATE//FILE_PLACEHOLDER/$current_file}"

    start_time=$(date "+%Y-%m-%d %H:%M:%S")
    echo "========================================"
    echo "[$start_time] ITERATION $iteration (LOOP 2)"
    echo "========================================"
    echo "Files remaining: $file_count"
    echo "Processing file: $current_file"
    echo "----------------------------------------"
    echo ""

    # Run Claude Code and capture output
    # The -p flag runs non-interactively and prints the response
    output=$(claude -p --dangerously-skip-permissions --model claude-opus-4-5-20251101 --max-turns 50 "$PROMPT" 2>&1)

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
        # Log failed file for debugging
        echo "[$end_time] === Trigger not found. Failed file: $current_file ==="
        echo "[$end_time] FAILED: $current_file" >> "$FAILED_LOG"
        echo "[$end_time] === Stopping. ==="
        break
    fi
done

echo "=== Script finished after $((iteration - 1)) iteration(s) ==="
