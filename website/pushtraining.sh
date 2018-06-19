#!/bin/sh
rsync -av --delete --exclude-from=push-exclude.txt . graham@51.141.48.142:/home/graham/theatrefest/training_website/
rsync -av --delete ./django_static/* graham@51.141.48.142:/home/graham/theatrefest/training_website/static
