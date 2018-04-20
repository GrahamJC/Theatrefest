#!/bin/sh
rsync -av --delete --exclude-from=push-exclude.txt . graham@51.141.48.142:/home/graham/theatrefest/website/
