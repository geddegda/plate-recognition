#!/bin/bash
RAM_DIR=/home/guillaume/ram_videos
HDD_DIR=/home/guillaume/videos

if [[ -d "$RAM_DIR" && -d "$HDD_DIR" ]];then
	echo " Source and target folder exist. OK."
else
	echo "Error: One or both folders are missing"
	exit 1
fi


while true; do
	file_count=$(ls -1 "$RAM_DIR" | wc -l)
	if [ "$file_count" -ge 60 ]; then
		echo "$(date): Copying $file_count files to HDD at $HDD_DIR from $RAM_DIR..."

		for f in "$RAM_DIR"/*; do
			cp "$f" "$HDD_DIR"/ && rm "$f"
		done

		echo "Done."

	fi
	sleep 20
done
