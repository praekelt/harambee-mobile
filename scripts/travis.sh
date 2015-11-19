#!/bin/bash

pwd
cp id_rsa.travis ~/.ssh
echo Host github.com >> ~/.ssh/config
echo "\tHostname ssh.github.com" >> ~/.ssh/config
echo "\tUser git" >> ~/.ssh/config
echo "\tPort 443" >> ~/.ssh/config
echo "\tIdentityFile ~/.ssh/id_rsa.travis" >> ~/.ssh/config

ls ~/.ssh
cat ~/.ssh/config
