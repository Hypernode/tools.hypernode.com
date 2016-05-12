DEPLOY_DIR="$(dirname "$0")"
host=178.62.221.43
tools/md_to_html.sh
rsync --exclude=.git --exclude-from=.gitignore --exclude=magerundumps/ --exclude=postdata/ --exclude=*.pyc --exclude=.idea -va $DEPLOY_DIR/../ root@$host:/srv/app/
ssh root@$host service uwsgi restart
