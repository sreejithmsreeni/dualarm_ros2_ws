#!/bin/bash

# --- 1. Launch the ROS 2 controller node ---
# This command *MUST* be the first one, as it triggers the ETHERCAT-OP thread.
# This assumes the ROS 2 node is the main command being prefixed.

# --- 2. Wait for the EtherCAT kernel thread to appear ---
sleep 5

# 3. Find the PID of the EtherCAT-OP kernel thread
# The '-o' flag finds the oldest thread (the master thread)
ETHERCAT_PID=$(pgrep -o "EtherCAT-OP")

if [ -n "$ETHERCAT_PID" ]; then
    echo "--- Setting Permanent RT Priority for ETHERCAT-OP (PID $ETHERCAT_PID) ---"

    # Set SCHED_FIFO Priority 95 and pin to Core 3
    sudo taskset -p 3 $ETHERCAT_PID
    sudo chrt -f -p 95 $ETHERCAT_PID

    echo "--- ETHERCAT-OP RT setup complete: Core 3, PRI 95 ---"
else
    echo "--- WARNING: ETHERCAT-OP thread not found after launch. RT setup failed. ---"
fi

# IMPORTANT: The script must then execute the actual command it was supposed to run.
# The ROS 2 launch system will automatically pass the executable and arguments
# as arguments to this wrapper script.
exec "$@"