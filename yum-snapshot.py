#!/usr/bin/python

import argparse
import config
import os
import time
import shutil
import subprocess


def addSnapshot( args ):
    source = getSnapshotSource( args.distro, args.release, args.arch )
    repoLocalDir = createRepoLocalDir( args.distro, args.release, args.arch )
    print 'Creating mirror'
    createLocalmirror( source, repoLocalDir )
    print 'Uploading to S3'
    uploadToS3( repoLocalDir, config.S3_BUCKET )
    shutil.rmtree( repoLocalDir )
    print 'Done.'
    print 'Repository base url is: <bucket_url>/%s' % os.path.basename( repoLocalDir )

def getSnapshotSource( distro, release, arch ):
    if distro == 'fedora':
        source = config.FEDORA_UPDATE_BASE_URL
    elif distro == 'centos':
        source = config.CENTOS_UPDATE_BASE_URL
    else:
        raise KeyError( 'Failed to find source url for %s distro' % distro )
    source = source.replace( '{release}', release )
    source = source.replace( '{arch}', arch )
    return source

def createRepoLocalDir( distrao, release, arch ):
    snapshotDir = time.strftime( "%Y-%m-%d-%H%M%S" ) + '-%s-%s-%s' % ( distrao, release, arch )
    path = os.path.join( os.getcwd(), snapshotDir )
    print path
    os.makedirs( path )
    return path

def createLocalmirror( source, destination ):
    cmd = 'rsync  -avSHP --delete --exclude "local*" --exclude "isos" %(src)s %(dst)s' % dict( src = source, dst = destination )
    subprocess.call( cmd, shell = True )

def uploadToS3( repoLocalDir, targetBucket ):
    cmd = 's3cmd sync --no-delete-removed %(src)s %(dst)s' % dict( src = repoLocalDir, dst = targetBucket )
    subprocess.call( cmd, shell = True )

def listAllSnapshots( dummy ):
    for entry in listBucket():
        if entry.endswith( '/' ):
            print entry.split( '/' )[3]

def listBucket():
    cmd = 's3cmd ls ' + config.S3_BUCKET
    out = subprocess.check_output( cmd, shell = True )
    return  out.split( '\n' )

if __name__ == '__main__':
    parser = argparse.ArgumentParser( description = 'handle yum frozen repository', usage = 'yum-snapshot' + '<action>' )
    subparsers = parser.add_subparsers( dest = 'action', help = 'sub-command help' )
    parser_add = subparsers.add_parser( 'add', help = 'add a yum update repository snapshot' )
    parser_add.add_argument( '-distro', help = 'the distribution that will be snapshot', default = 'centos' )
    parser_add.add_argument( '-release', help = 'the release that will be snapshot', default = '7' )
    parser_add.add_argument( '-arch', help = 'the architecture that will be snapshot', default = 'x86_64' )

    parser_list = subparsers.add_parser( 'list', help = 'list all available snapshots' )
    args = parser.parse_args()

    choices = { 'add' : addSnapshot,
                'list' : listAllSnapshots
              }
    action = args.action
    choices[ action ]( args )
