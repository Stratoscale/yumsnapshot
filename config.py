sources = { 'fedora' : 'rsync://dl.fedoraproject.org/fedora-enchilada/linux/%(repo)s/%(release)s/%(arch)s/',
            'centos' : 'rsync://centos.eecs.wsu.edu/centos/%(release)s/%(repo)s/%(arch)s/'
          }
S3_BUCKET = 's3://yumfreeze.com'
