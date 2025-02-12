from fabric.api import *
import fabric.contrib.project as project
import os

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'public'
DEPLOY_PATH = env.deploy_path

# Remote server configuration
production = 'root@localhost:22'
dest_path = '/var/www'

# Rackspace Cloud Files configuration settings
env.cloudfiles_username = 'my_rackspace_username'
env.cloudfiles_api_key = 'my_rackspace_api_key'
env.cloudfiles_container = 'my_cloudfiles_container'


def clean():
    if os.path.isdir(DEPLOY_PATH):
        local('rm -rf {deploy_path}'.format(**env))
        local('mkdir {deploy_path}'.format(**env))


def build():
    local('python ./tools/prepare_xep_list.py')
    local('python ./tools/lint-list.py clients.json')
    local('python ./tools/lint-list.py servers.json')
    local('python ./tools/lint-list.py libraries.json')
    local('hugo')


def rebuild():
    clean()
    build()


def serve():
    local('cd {deploy_path} && python -m SimpleHTTPServer'.format(**env))


def reserve():
    build()
    serve()


def preview():
    local('hugo server')


def cf_upload():
    rebuild()
    local('cd {deploy_path} && '
          'swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
          '-U {cloudfiles_username} '
          '-K {cloudfiles_api_key} '
          'upload -c {cloudfiles_container} .'.format(**env))


@hosts(production)
def publish():
    rebuild()
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )
