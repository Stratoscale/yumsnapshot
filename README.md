yum-snapshot

A command line tool to create a frozen YUM Repository 

Introduction

YUM is a repository management tool which will fetch the appropriate package
for your particular version of Linux(along with all other required packages).
YUM will fetch different packages from appropriate different repositories.
This tool will create a complete yum repository snapshot of the requested update repository on AWS S3.

In order to use this tool you need to create a bucket on AWS s3 and configure the bucket for Website Hosting

usage: 

    ./yum-snapshot.py add -distro <centos> -release <7> -arch <x86_64>
    ./yum-snapshot.py list 

To start using the newly created repository, create a <reponame>.repo file under /etc/yum.repos.d/

