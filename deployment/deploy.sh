host=178.62.221.43
tools/md_to_html.sh
rsync --exclude=.git --exclude=magerundumps/ --exclude=postdata/ --exclude=*.pyc --exclude=.idea -va ~/code/modules.hypernode.com/ root@$host:/srv/app/
#rsync --exclude=.git --exclude=postdata/ --exclude=*.pyc --delete --exclude=.idea -va ~/code/modules.hypernode.com/ root@$host:/srv/magmodules/
ssh root@$host service uwsgi restart
