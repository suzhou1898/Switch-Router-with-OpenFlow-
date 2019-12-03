#! /bin/bash

sudo mn -c
sudo mn --custom ~/topology2.py --topo topology2 --mac --controller=remote,ip=127.0.0.1,port=6633