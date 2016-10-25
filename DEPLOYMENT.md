# Dev install

Python required. At Ubuntu 16.04:

```
git clone https://github.com/Hypernode/tools.hypernode.com.git
mkvirtualenv -a tools.hypernode.com tools.hypernode.com --python=`which python3`
cd tools.hypernode.com
pip install -r requirements.txt
```

# New Magento version?

```
tools/patch_spreadsheet_to_json.py
```

Inspect changes to static/required_magento_patches.json & git commit.

Run

```
git commit -am "New Magento version"
git push origin
deployment/deploy.sh
```

Test

```
curl https://tools.hypernode.com/patches/community/1.9.2.0
magerun hypernode:patches:list
```

