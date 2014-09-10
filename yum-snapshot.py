import argparse
import config
import time
import os
from strato.common import ssh

def addSnapshot( args ):
    distro =  args.distro
    print distro
    if distro == 'fedora':
        source = os.path.join( config.FEDORA_UPDATE_BASE_URL, args.release, args.arch )
        print source
    elif distro == 'centos':
        source = config.CENTOS_UPDATE_BASE_URL.replace( '{release}', args.release )
        source = os.path.join( source, args.arch )
    else:
        print 'please add source url for %s distro' % distro
    repoLocalDir = getRepoLocalDir( distro, args.release, args.arch )
    print downloadRPMS( source, repoLocalDir )
    print createRepoMetadata( repoLocalDir )
    print uploadToS3( repoLocalDir )

def getRepoLocalDir( distrao, release, arch ):
    snapshotDir = time.strftime( "%Y-%m-%d-%H%M%S" ) + '-%s-%s-%s' % ( distrao, release, arch )
    return os.path.join( 'yumsnapshot', snapshotDir )

def downloadRPMS( source, targetDir ):
    rpmsDir =  os.path.join( targetDir, 'rpms' )
    os.makedirs( rpmsDir )
    excludeDirs = 'debug, drpms, repodata'
    cmd = [ 'wget', '--no-directories', '--mirror', '--convert-links', '--adjust-extension', \
            '--page-requisites', '--no-parent', '--directory-prefix=', targetDir, '--exclude-directories=', excludeDirs,   source ]
    return cmd
    #subprocess.call( cmd, shell = True)

def createRepoMetadata( repoLocalDir ):
    cmd = [ 'createrepo', '--database', '--outputdir',  repoLocalDir ]
    return cmd

def runInEC2( commands ):
    sshClient = ssh.SSH( hostname = config.HostnameForSSH,
                         useggrname = config.UserForSSH,
                         key = config.KeyForSSH )
    sshClient.connect()
    for cmd in commands:
        sshClient.runScript( cmd )

def uploadToS3( repoLocalDir ):
    targetBucket = 's3://yum_freeze'
    cmd = 's3cmd sync --no-delete-removed %(src)s %(dst)s' % dict( src = repoLocalDir, dst = targetBucket )
    return cmd

def listSnapshots():
    pass
if __name__ == '__main__':
    parser = argparse.ArgumentParser( description = 'handle yum frozen repository', usage = 'yum-snapshot' + '<action>' )
    subparsers = parser.add_subparsers( dest = 'action', help = 'sub-command help' )
    parser_add = subparsers.add_parser( 'add', help = 'add a snapshot of a repository' )
    parser_add.add_argument( 'distro', help = 'the distribution that will be snapshot' )
    parser_add.add_argument( '-release', help = 'the release that will be snapshot', default = '19' )
    parser_add.add_argument( '-arch', help = 'the architecture that will be snapshot', default = 'x86_64' )

    parser_list = subparsers.add_parser( 'list', help = 'list all available snapshots' )
    args = parser.parse_args()

    choices = { 'add' : addSnapshot,
                'list' : listSnapshots
              }
    action = args.action
    choices[ action ]( args )
