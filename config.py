sources = { 'fedora' : 'rsync://dl.fedoraproject.org/fedora-enchilada/linux/updates/%(release)s/%(arch)s/',
            'centos' : 'rsync://centos.eecs.wsu.edu/centos/%(release)s/updates/%(arch)s/'
          }
S3_BUCKET = 's3://yumfreeze.com'
