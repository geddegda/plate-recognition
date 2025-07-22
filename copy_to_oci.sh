#!/bin/bash
HDD_DIR=/home/guillaume/videos

while true; do
	if [ -n "$(find "$HDD_DIR" -maxdepth 1 -type f)" ]; then

		for f in "$HDD_DIR"/*; do
			oci os object put --bucket-name lab_videos --file "$f"
			if [ $? -eq 0 ]; then
				echo "Uploaded: $f"
			else
				echo "Failed to upload $f to OCI"
			fi
		done
		echo "Done uploading to OCI."
	fi
	sleep 10
done
