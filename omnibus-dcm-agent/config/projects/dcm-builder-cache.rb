#
# Copyright 2015 YOUR NAME
#
# All Rights Reserved.
#

name "dcm-builder-cache"
maintainer "DCM"
homepage "https://enstratius.com"

install_dir "/opt/#{name}"

build_version "0.7.0" # SEARCH_TOKEN do not delete
#build_version Omnibus::BuildVersion.semver
build_iteration 1

# Creates required build directories
dependency "preparation"
dependency "puppet-gem"
dependency "ec2-ami-tools"
dependency "zlib"
dependency "sqlite"
dependency "python"
dependency "pip"
dependency "virtualenv"
dependency "pyyaml"

# Version manifest file
dependency "version-manifest"

exclude "**/.git"
exclude "**/bundler/git"
