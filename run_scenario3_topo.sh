#! /bin/bash

sudo mn -c
sudo mn --custom ~/topology3.py --topo topology3 --mac --controller=remote,ip=127.0.0.1,port=6633