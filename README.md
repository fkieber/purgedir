# purgedir
Remove files on size or age.

## Usage
```
Syntaxe :  purge-dir.py  [-h | --help] [Options] path_to_purge
Options :
-h or --help : Print this help.
-d n = Number of retention days. All files older then n days are
       deleted.
-s n = Maximal size. Default size is in bytes.
       Size can be suffixed with K for Kb, M for Mb,
       G for Gb or T for Tb.
       For example -s8M corresponds to 8 Mb or 8,368,608 bytes.
       The oldest files are deleted so that the total directory 
       size does not exceed n.
-t or --test : Do not delete files.
-v : Show files to be deleted.
path_to_purge = path to the directory to purge.
-d AND -s can be given simultaneously. In this case the age
       is taken into account first.
```

## Implementation
Simply copy the script into `/usr/local/bin` for exemple and make it executable.

## To do
- Translate from French
- Add `-r recurse into sub-directories`option.
- Ability to specify the size in % of the underlyinf file system.
- Use of `argparse` insted of `getopt`.
