#!/bin/sh

# Software Name : cpu_usage.sh
# Software Version : 0.0.1
# SPDX-FileCopyrightText: Copyright (c) 2024 Orange SA
# SPDX-License-Identifier: MIT
#
# This software is distributed under the MIT license,
# see the "LICENSE.md" file for more details or https://opensource.org/license/MIT
#
# Authors: Maximilien Baumann
# Software description: script to log into a file the cpu usage of the prpl box


# keep IFS, as we need to split once by space and one by line we have to change it many time
OIFS=$IFS
# file to save values
output_file="/tmp/cpu_usage.csv"
# head of CSV file, add column by cpu
# need to split only by line and not by space
file_head="Time,Global cpu"
IFS=$(printf '\n.'); IFS=${IFS%.}
for cpu in $(grep '^cpu[0-9]' /proc/stat); do
    # back to normal split
    IFS=$OIFS
    set -- $cpu
    cpu_id=$1
    file_head="$file_head,$cpu_id"
    # back to space split
    IFS=$(printf '\n.'); IFS=${IFS%.}
done
IFS=$OIFS
echo "$file_head" > "$output_file"

# Calculate global cpu usage
calculate_cpu_usage() {
    cpu_line=$1
    set -- $cpu_line
    cpu_id=$1
    user=$2
    nice=$3
    system=$4
    idle=$5
    iowait=$6
    irq=$7
    softirq=$8
    steal=$9

    total_time=$((user + nice + system + idle + iowait + irq + softirq + steal))
    if [ $total_time -ne 0 ]; then
        idle_time=$idle
        cpu_usage=$(awk -v a="$total_time" -v b="$idle_time" 'BEGIN { printf "%s", (a-b) * 100 / a }' </dev/null)
    else
        cpu_usage="0.00"
    fi
    echo "$cpu_usage"
}


display_cpu_usage() {
    # date to fill the file
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    # global cpu usage
    cpu_global=$(head -n 1 /proc/stat)
    echo $cpu_global
    global_usage=$(calculate_cpu_usage "$cpu_global")
    echo "global CPU usage : $global_usage%"
    # keep it for file writing
    cpu_usages_fileline="$global_usage"

    # loop on all cpu to have usage details
    # need to split only by line and not by space
    IFS=$(printf '\n.'); IFS=${IFS%.}
    for cpu in $(grep '^cpu[0-9]' /proc/stat); do
        # back to normal split for the set command
        IFS=$OIFS
        cpu_usage_formatted=$(calculate_cpu_usage "$cpu")
        # add it to the line for the file
        cpu_usages_fileline="$cpu_usages_fileline,$cpu_usage_formatted"
        # for next loop, back to line split
        IFS=$(printf '\n.'); IFS=${IFS%.}
    done
    echo "result :$timestamp  $cpu_usages_fileline"
    # back to normal split
    IFS=$OIFS
    echo "$timestamp,$cpu_usages_fileline" >> "$output_file"
}

# calcuate and who value every second
while true; do
    clear
    display_cpu_usage
    sleep 1
done
