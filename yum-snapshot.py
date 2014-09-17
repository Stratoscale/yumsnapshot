#!/usr/bin/python

import argparse
import config
import logging
import os
import time
import re
import shutil
import subprocess


def createSnapshot( distro, release, arch, cwd = None ):
    source = getSnapshotSource( distro, release, arch )
    snapshotDirName = '%s-%s-%s-updates/%s' % ( distro, release, arch, time.strftime( "%Y-%m-%d-%H%M%S" ))
    repoLocalDir = createRepoLocalDir( snapshotDirName, cwd )
    logging.info( 'Creating mirror' )
    createLocalmirror( source, repoLocalDir )
    logging.info( 'Uploading to S3' )
    uploadToS3( repoLocalDir, config.S3_BUCKET )
    shutil.rmtree( repoLocalDir )
    logging.info( 'Done.' )
    logging.info( 'Repository base url is: <bucket_url>/' + snapshotDirName )

def getSnapshotSource( distro, release, arch ):
    source = config.sources[distro]
    return source % dict( release = release, arch = arch )

def createRepoLocalDir( snapshotDir, cwd = None ):
    if not cwd:
        cwd = os.getcwd()
    path = os.path.join( cwd, snapshotDir )
    os.makedirs( path )
    logging.info( 'Created %s as repo local directory' % path )
    return path

def createLocalmirror( source, destination ):
    cmd = 'rsync  -avSHP --delete --exclude "local*" --exclude "isos" %(src)s %(dst)s' % dict( src = source, dst = destination )
    subprocess.check_call( cmd, shell = True )

def uploadToS3( repoLocalDir, targetBucket ):
    src = os.path.dirname( repoLocalDir  )
    cmd = 's3cmd sync --no-delete-removed %(src)s %(dst)s' % dict( src = src, dst = targetBucket )
    subprocess.check_call( cmd, shell = True )

def listAllSnapshots():
    for entry in listBucket():
        print entry

def listBucket():
    cmd = 's3cmd ls '
    out = subprocess.check_output( cmd + config.S3_BUCKET, shell = True )
    ret = []
    for entry in  out.split( '\n' ):
        if entry.endswith( '/' ):
            ret.append( subprocess.check_output( cmd + entry.split( 'DIR' )[1], shell = True ))
    return ret


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser( description = 'handle yum frozen repository', usage = 'yum-snapshot' + '<action>' )
    subparsers = parser.add_subparsers( dest = 'action', help = 'sub-command help' )
    parser_add = subparsers.add_parser( 'create', help = 'create a yum update repository snapshot' )
    parser_add.add_argument( '-distro', help = 'the distribution that will be snapshot, defaults to centos ', default = 'centos' )
    parser_add.add_argument( '-release', help = 'the release that will be snapshot, defaults to 7', default = '7' )
    parser_add.add_argument( '-arch', help = 'the architecture that will be snapshot, defaults to x86_64 ', default = 'x86_64' )
    parser_add.add_argument( '-cwd', help = 'the working directory, defaults to getcwd()', default = None )

    parser_list = subparsers.add_parser( 'list', help = 'list all available snapshots' )
    args = parser.parse_args()

    if args.action == 'create':
        createSnapshot( args.distro, args.release, args.arch, args.cwd  )
    elif args.action == 'list':
        listAllSnapshots()
