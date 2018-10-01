## description

cherokee2nginx.py is a script for the partial conversion of Cherokee
configuration files into the Nginx equivalents. Some manual editing of the
resulting file will be required. The supported configuration keys are limited
to what the author(s) needed. Contributions are welcome.

Before running the script you might want to upgrade the cherokee.conf file:
```sh
/usr/share/cherokee/admin/upgrade_config.py cherokee.conf
```
The script was tested with the config version 1002103.

## usage

```sh
$ ./cherokee2nginx.py --help
usage: cherokee2nginx.py [-h] [--cherokee-admin-path <dir>] [-v]
                         <in_file> <out_file>

Convert a Cherokee configuration file to its Nginx equivalent.

positional arguments:
  <in_file>             cherokee.conf
  <out_file>            nginx.conf (will be overwritten)

optional arguments:
  -h, --help            show this help message and exit
  --cherokee-admin-path <dir>
                        path to the Cherokee admin directory (default:
                        /usr/share/cherokee/admin)
  -v, --verbose         increase output verbosity (default: False)
```

## requirements

- Python 2
- [Cherokee][1] (some Python modules from cherokee-admin are used to parse the configuration file)

## further reading

- [list of equivalent options/concepts][2] - a very useful blog post from April 2013 by David Beitey
- [official Cherokee configuration file documentation][3]

## license

Mozilla Public License Version 2.0

## credits

- author: Ștefan Talpalaru <stefantalpalaru@yahoo.com>

- homepage: https://github.com/stefantalpalaru/cherokee2nginx


[1]: http://cherokee-project.com/
[2]: http://davidjb.com/blog/2013/04/switching-to-nginx-from-cherokee-techincal-guide/
[3]: http://cherokee-project.com/doc/dev_cherokee.conf.html

