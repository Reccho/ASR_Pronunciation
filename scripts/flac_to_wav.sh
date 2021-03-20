#!/bin/bash

for file in `find . -name "*.flac" -type f`; do
	fpath=$(dirname $file)
	base=$(basename ${file%.*})
    ffmpeg -i $file -ar 16000 -ac 1 $fpath/$base.wav
    rm $file
done
