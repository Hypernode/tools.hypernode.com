![Sponsored by Hypernode](hypernode-logo.png)

# Magento Labs (beta)

A collection of tools to help manage multiple Magento installations.

## Magerun interface

Elgento's Peter Jaap has written an [excellent plugin for Magerun](https://github.com/Hypernode/hypernode-magerun):

![Magerun sys:modules:list-updates](https://cloud.githubusercontent.com/assets/431360/12973661/3d7842ec-d0ae-11e5-9ebb-40da2ceac3e3.png)

![Magerun sys:info:patches](https://cloud.githubusercontent.com/assets/431360/12973660/3d77a648-d0ae-11e5-8a74-ddefb0e90d81.png)

## API / JSON interface

But you can also integrate this into your own tools.

### Find outdated modules

Example usage:
```
$ n98-magerun sys:modules:list --format=json | \
    curl -d @- -X POST -H "Content-Type: application/json" \
    http://tools.hypernode.com/modules/magerun.txt

Name                             Current      Latest
==============================================================
Aoe_Scheduler                    0.4.3        1.3.1
Aoe_TemplateHints                0.3.0        0.4.3
Hans2103_HideCompare             1.0          1.0.2
Lesti_Fpc                        1.2.0        1.4.4
Magestore_Magenotification       0.1.3        0.1.4
Mirasvit_SearchLandingPage       1.0.0        1.0.1
Mollie_Mpm                       4.1.5        4.1.9
TIG_PostNL                       1.3.1        1.7.2
Yireo_DeleteAnyOrder             0.11.2       0.12.3
```

See if newer versions exist for your currently installed Magento 1 modules (local & community). I hear you say, _Magento Connect already does this?_ Not quite, as Magento Connect only contains a subset of all Magento modules (Firegento anyone?).

The dataset is crowdsourced: it will report the latest version of any module _as seen in the wild_. This does not necessarily mean a newer version is publicly available, just that it exists.

As of Feb 2016, it contains version information from a few hundred installations.

You can also use the `/modules/magerun.json` endpoint.

### Determine required patches

Magento's Piotr Kaminski maintains an [excellent spreadsheet](https://docs.google.com/spreadsheets/d/1MTbU9Bq130zrrsJwLIB9d8qnGfYZnkm4jBlfNaBF19M/pubhtml?widget=true) (originally by John Knowles) which links Magento versions with required patches.

Use this API to query it:

```
$ curl http://tools.hypernode.com/patches/community/1.9.2.0
{"required": [
        "SUPEE-6482",
        "SUPEE-6788",
        "SUPEE-7405"
]}

$ curl http://tools.hypernode.com/patches/enterprise/1.10.0.1
{"required": [
        "SUPEE-1533",
        "SUPEE-2750",
        "SUPEE-5388",
        "SUPEE-5994",
        "SUPEE-6285",
        "SUPEE-6482",
        "SUPEE-6788",
        "SUPEE-7405",
        "Zend Security Upgrade"
]}
```

## Contact

[hypernode@byte.nl](mailto:hypernode@byte.nl) or fork me at Github
