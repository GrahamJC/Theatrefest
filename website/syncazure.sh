#!/bin/sh
rsync -av --delete --exclude-from=rsync-exclude.txt . graham@51.141.48.142:/home/graham/theatrefest/website/
