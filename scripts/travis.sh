#!/bin/bash

pwd
cp id_rsa.travis ~/.ssh
chmod 600 ~/.ssh/id_rsa.travis
echo Host github.com >> ~/.ssh/config
echo -e "\tHostname ssh.github.com" >> ~/.ssh/config
echo -e "\tUser git" >> ~/.ssh/config
echo -e "\tPort 443" >> ~/.ssh/config
echo -e "\tIdentityFile ~/.ssh/id_rsa.travis" >> ~/.ssh/config

ls ~/.ssh
cat ~/.ssh/config
