
#!/bin/bash

# Check if tmux is installed
if ! command -v tmux &> /dev/null
then
    echo "tmux is not installed. Please install it (e.g., sudo apt install tmux on Debian/Ubuntu)."
    exit 1
fi

# Start tmux in a new session
tmux new-session -d -s watchtower

# Split the window horizontally
tmux split-window -h

# Select the first pane (left side)
tmux select-pane -t 0

# Run the server process in the first pane
tmux send-keys "python app.py" C-m

# Select the second pane (right side)
tmux select-pane -t 1

# Start each agent in its own pane (vertical splits)
agent_types=("SecOps" "DevOps" "CloudSec" "AISec" "Architect")
pane_id=1 # Start at 1

for agent_type in "${agent_types[@]}"; do
    if [ "$pane_id" -gt 1 ]; then
        tmux split-window -v -t 1
        pane_id=$(($pane_id+1))
        tmux select-pane -t "$pane_id"
    fi
    tmux send-keys "python agent.py --agent_type $agent_type" C-m
done


# Attach to the tmux session
tmux attach-session -t watchtower
```
