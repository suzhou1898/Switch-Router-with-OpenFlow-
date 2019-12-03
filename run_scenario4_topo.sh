#! /bin/bash

sudo mn -c
sudo mn --custom ~/topology4.py --topo topology4 --mac --controller=remote,ip=127.0.0.1,port=6633