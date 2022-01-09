#!/bin/sh
[ $# -eq 0 ] && set - autonom.tar.gz
#
# Create base tar file
#
tarball="$1"

workdir=$(mktemp -d)
trap "rm -rf $workdir" EXIT

cp -a *.py static views $workdir
rm -f $workdir/bottle.py
cp -a $(readlink -f bottle.py) $workdir


tar --exclude-vcs -zcf "$tarball" \
	-C $workdir $(cd $workdir && ls -1)

