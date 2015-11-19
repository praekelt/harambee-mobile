#!/bin/bash

cp ../id_rsa.travis ~/.ssh
echo Host github.com >> ~/.ssh/config
echo    Hostname ssh.github.com >> ~/.ssh/config
echo    User git >> ~/.ssh/config
echo    Port 443 >> ~/.ssh/config
echo    IdentityFile ~/.ssh/id_rsa.travis >> ~/.ssh/config

ls ~/.ssh
cat ~/.ssh/config
