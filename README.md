# Composer Tools

## Introduction

This tool is a convenient helper that lets you easily switch from a repository 
version of a Composer package (VCS repository or Packagist) to a local version 
on your local file system (and back). It works by replacing the directory that 
Composer adds with a symbolic link. Why? [Read this blog post.](#) Isn't it a 
hack? Sure it is, but it works and there seems to be no convenient way of doing 
this right now (AFAIK). This tool doesn't do any magic; it just automates a 
series of simple commands for you.

#### Requirements

Requires Python 3.7. Currently untested on Windows. If you test it, please let me 
know how it goes.

#### Warning!

This is just a quick tool that I hacked together, so use at your own risk! 
If you want to check how it works under the hood, then I encourage you to 
take a moment to read through the source code.

## Installation

### Mac/Linux

1. Clone the repository.

```
git checkout https://github.com/codingexplained/composer-tools.git
```

2. Copy `composer-tools.py` into place (and rename it).

```
cp composer-tools.py /usr/local/bin/composer-tools
```

3. Give the file executable permission.

```
chmod +x /usr/local/bin/composer-tools
```

### Windows

N/A

## Setup

Within your project's root directory, create a file named `composer.dev.json`, 
where you need to configure where packages should be symlinked to locally.

```
{
  "packages": {
    "example/package": "/path/to/example/package"
  }
}
```

You can also specify relative paths instead, which are relative to the project root.

```
{
  "packages": {
    "example/package": "../../example/package"
  }
}
```

Apart from often looking cleaner, relative paths have an added advantage when using 
Docker containers, for instance; if you have mounted your source code with a volume 
and used absolute paths, the symlink is going to be invalid within your container, 
because the absolute path on the host OS most likely doesn't exist within the 
container. By using relative paths, all you need to do, is to mount the packages 
relative to the project root within the container. 

## Usage

```
usage: composer-tools [-h] [--config CONFIG]
                      [--packages PACKAGES [PACKAGES ...]] [--force-absolute]
                      {ln,reset}

Switch between local and repository Composer package versions.

positional arguments:
  {ln,reset}            The action to perform

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Specify the path to the configuration file instead of
                        using the default location
  --packages PACKAGES [PACKAGES ...]
                        Specify packages for which the action should be performed. 
                        Currently only supported for the "ln" action.
  --force-absolute      Force generated paths to be absolute
```

### Symlinking local package

To symlink packages to their local versions instead of the repository versions, use the following command:

```
composer-tools ln
```

### Symlinking specific packages

By default, all packages defined within the configuration file are symlinked. 
You may, however, specify one or more packages instead.

```
composer-tools ln --packages vendor/package1 vendor/package2
```

**NOTE:** This only works with the `ln` command. This is because the `reset` 
command runs `composer install`, which reverts all packages to those defined 
within the `composer.lock` file. Unfortunately the `install` command does not 
accept specific packages as an argument, and we don't want to run the 
`update` command and disrespect what is written within `composer.lock`.

### Resetting to repository packages

To reset packages to the version defined within `composer.lock`, run the following command:

```
composer-tools reset
```

This removes the symbolic links to the local packages and runs `composer install`. 

### Specifying the configuration file path

By default, the tool looks for a file named `composer.dev.json` in the current 
working directory (the project root). You can, however, specify the path to the 
configuration file instead.

```
composer-tools ln --config /path/to/config.json
```

### Forcing absolute paths

Given that you used relative paths within your configuration file, the generated 
symlinks are also going to use relative paths. If you want to force all paths to 
be absolute, you can specify the `force-absolute` flag. This will make all paths 
absolute, even if a configured path is relative.

```
composer-tools ln --force-absolute
```