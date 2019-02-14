#!/usr/bin/env python

from enum import Enum
from typing import List
import sys
import os.path
import shutil
import subprocess
import argparse
import json


class Action(Enum):
    LINK = 'ln'
    RESET = 'reset'


def invoke_composer(params: List[str], has_global: bool = True) -> subprocess.CompletedProcess:
    if has_global:
        command = 'composer'
    else:
        command = 'php composer.phar'

    command += ' ' + ''.join(params)
    print(command)

    return subprocess.run(command, check=True, shell=True)


cwd = os.getcwd()
parser = argparse.ArgumentParser(description='Switch between local and repository Composer package versions.')
parser.add_argument('action', choices=[e.value for e in Action], help='The action to perform')
parser.add_argument('--config',
                    default=cwd + '/composer.dev.json',
                    help='Specify the path to the configuration file instead of using the default location')
parser.add_argument('--packages',
                    nargs='+',
                    help='Specify packages for which the action should be performed. Currently only supported for the "ln" action.')
parser.add_argument('--composer-install-options',
                    nargs='+',
                    default=[],
                    help='Specify options passed to "composer install".')
parser.add_argument('--force-absolute', action='store_true', help='Force generated paths to be absolute')

args = parser.parse_args()
has_global_composer = shutil.which('composer') is not None

if not os.path.isfile(cwd + '/composer.json'):
    print('composer.json must be present in the current working directory!')
    sys.exit()

if not os.path.isdir(cwd + '/vendor'):
    print("'vendor' directory not found! Try running 'composer install'?")
    sys.exit()

if not has_global_composer:
    if not os.path.isfile(cwd + '/composer.phar'):
        print('Composer must be installed globally, or composer.phar must be present in the current working directory!')
        sys.exit()

if not os.path.isfile(args.config):
    print('Configuration file not found at ' + args.config + '!')
    sys.exit()

with open(args.config, 'r') as fh:
    config = json.load(fh)

if args.packages:
    if args.action != Action.LINK.value:
        print('The --packages argument is currently only supported for the "ln" action!')
        sys.exit()

    # Load the configurations for the specified packages.
    packages = {}

    for p in args.packages:
        try:
            packages[p] = config['packages'][p]
        except KeyError:
            print('Configuration for package', p, 'not found in', args.config)
            sys.exit()
else:
    # Default to all configured packages.
    packages = config['packages']

for full_package in packages:
    developer, package_name = full_package.split('/')
    package_path = cwd + '/vendor/' + full_package
    target_path = packages[full_package]

    if not os.path.isabs(target_path):
        # The pass is relative.
        if args.force_absolute:
            # Make the path absolute.
            target_path = cwd + '/' + target_path
        else:
            # Keep the path relative; make it relative to the symlink location instead of project root.
            target_path = '../../' + target_path

    if os.path.isdir(package_path) and not os.path.islink(package_path) and args.action == Action.LINK.value:
        print('Removing', full_package)
        shutil.rmtree(package_path)

    if os.path.islink(package_path):
        print('Removing', full_package)
        os.unlink(package_path)

    if args.action == Action.LINK.value:
        print('Symlinking', 'vendor/' + full_package, 'to', target_path)
        os.symlink(target_path, package_path)

if args.action == Action.LINK.value:
    invoke_composer(['dump-autoload'])
else:
    invoke_composer(['install', ' --'.join([''] + args.composer_install_options)])
