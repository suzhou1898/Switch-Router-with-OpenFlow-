++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
			EE555 - Fall 2019 - Major Project - Design of OpenFlow controller using Python POX Library

							README File
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

+++++
TEAM
+++++
[Team Memeber 2 Name and USC email ID]
Haochen Xie, 4759523759
[Team Memeber 2 Name and USC email ID] 
Junquan Yu, 3372029142
+++++++++++++++++++++++++++++++
Files Submitted in the package
+++++++++++++++++++++++++++++++
[List of all the files submitted in the zip folder and a one line description of each file]
of_tutorial.py
controller2.py
controller3.py
controller4.py
controller5.py
topology2.py
topology3.py
topology4.py
run_scenario1_control.sh
run_scenario2_control.sh
run_scenario3_control.sh
run_scenario4_control.sh
run_scenario5_control.sh
run_scenario1_topo.sh
run_scenario2_topo.sh
run_scenario3_topo.sh
run_scenario4_topo.sh
run_scenario5_topo.sh
my_files.sh
Readme.txt
Report.pdf
+++++++++++++++++++++++++++++++
Important Instruction on Copy Files
+++++++++++++++++++++++++++++++
Uploaded files including scripts to copy all files and start all topologies and controllers. There are also separate instructions on doing this using command line, but I recommend you to use scripts.

First, upload all files on VM in any folder, e.g. ~/my_submit
Next, cd to that folder, input 
	chmod +x *.sh
Next, input following commands to copy all files to proper paths from this folder
	./my_files.sh
	
	If the above script does not work, then do these:
		cp ./topology*.py ~/
		cp ./run_scenario*.sh ~/
		cp ./controller*.py ~/pox/pox/misc/
Next, cd to root
	cd ~/

Now this folder contains files like run_scenario1_topo.sh and run_scenario1_control.sh. These files will help you to run all topologies and controllers for each scenario.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
							Scenario 1
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[List of files that are to be used to execute scenario 1]
of_tutorial.py
++++++++++++++++++++++
Location to copy files
++++++++++++++++++++++
<file_name> - <Location to copy>
[Destination to be provided for each file that is relevant to scenario 1]
of_tutorial.py - /home/mininet/pox/pox/misc/of_tutorial.py
run_scenario1_control.sh - /home/mininet/run_scenario1_control.sh
run_scenario1_topo.sh - /home/mininet/run_scenario1_topo.sh
++++++++++++++++
Commands to Run:
++++++++++++++++
[Any special instructions we need to follow before running commands you will mention below for scenario 1]
make sure that execute the command 
	./run_scenario1_control.sh
before the command
	./run_scenario1_topo.sh

[List of commands to run before we execute the test cases of scenario 1]
open two SSH terminal for Mininet, in the first terminal, run
./run_scenario1_control.sh
in the second terminal, run:
./run_scenario1_topo.sh

or if the above scripts do not work, do the following:

~/pox/pox.py log.level --DEBUG misc.of_tutorial
sudo mn --topo single,3 --mac --controller remote --switch ovsk


+++++++++++++++++++++++++++++++++
Special Notes or any observations  
+++++++++++++++++++++++++++++++++
[Any special notes or observations that we need to take care while evaluating scenario 1]
Null
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
							Scenario 2
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[List of files that are to be used to execute scenario 2]
topology2.py controller2.py
++++++++++++++++++++++
Location to copy files
++++++++++++++++++++++
<file_name> - <Location to copy>
[Destination to be provided for each file that is relevant to scenario 2]
topology2.py - /home/mininet/topology2.py
controller2.py - /home/mininet/pox/pox/misc/controller2.py
run_scenario2_control.sh - /home/mininet/run_scenario2_control.sh
run_scenario2_topo.sh - /home/mininet/run_scenario2_topo.sh
++++++++++++++++
Commands to Run:
++++++++++++++++
[Any special instructions we need to follow before running commands you will mention below for scenario 2]
make sure that execute the command "./run_scenario2_control.sh" before the command "./run_scenario2_topo.sh"

[List of commands to run before we execute the test cases of scenario 2]
open two SSH terminal for Mininet, in the first terminal, run:
./run_scenario2_control.sh
in the second terminal, run:
./run_scenario2_topo.sh

or if the above scripts do not work, do the following:

~/pox/pox.py log.level --DEBUG misc.controller2
sudo mn --custom ~/topology2.py --topo topology2 --mac --controller=remote,ip=127.0.0.1,port=6633

+++++++++++++++++++++++++++++++++
Special Notes or any observations
+++++++++++++++++++++++++++++++++
[Any special notes or observations that we need to take care while evaluating scenario 2]
Null
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
							Scenario 3
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[List of files that are to be used to execute scenario 3]

++++++++++++++++++++++
Location to copy files
++++++++++++++++++++++
<file_name> - <Location to copy>
[Destination to be provided for each file that is relevant to scenario 3]
topology3.py - /home/mininet/topology3.py
controller3.py - /home/mininet/pox/pox/misc/controller3.py
run_scenario3_control.sh - /home/mininet/run_scenario3_control.sh
run_scenario3_topo.sh - /home/mininet/run_scenario3_topo.sh
++++++++++++++++
Commands to Run:
++++++++++++++++
[Any special instructions we need to follow before running commands you will mention below for scenario 3]
make sure that execute the command "./run_scenario3_control.sh" before the command "./run_scenario3_topo.sh"

[List of commands to run before we execute the test cases of scenario 3]
open two SSH terminal for Mininet, in the first terminal, run:
./run_scenario3_control.sh
in the second terminal, run:
./run_scenario3_topo.sh

or if the above scripts do not work, do the following:

~/pox/pox.py log.level --DEBUG misc.controller3
sudo mn --custom ~/topology3.py --topo topology3 --mac --controller=remote,ip=127.0.0.1,port=6633


+++++++++++++++++++++++++++++++++
Special Notes or any observations
+++++++++++++++++++++++++++++++++
[Any special notes or observations that we need to take care while evaluating scenario 3]
Null
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
							Scenario 4
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[List of files that are to be used to execute scenario 4]

++++++++++++++++++++++
Location to copy files
++++++++++++++++++++++
<file_name> - <Location to copy>
[Destination to be provided for each file that is relevant to scenario 4]
topology4.py - /home/mininet/topology4.py
controller4.py - /home/mininet/pox/pox/misc/controller4.py
run_scenario4_control.sh - /home/mininet/run_scenario4_control.sh
run_scenario4_topo.sh - /home/mininet/run_scenario4_topo.sh
++++++++++++++++
Commands to Run:
++++++++++++++++
[Any special instructions we need to follow before running commands you will mention below for scenario 4]
make sure that execute the command "./run_scenario4_control.sh" before the command "./run_scenario4_topo.sh"
[List of commands to run before we execute the test cases of scenario 4]
open two SSH terminal for Mininet, in the first terminal, run:
./run_scenario4_control.sh
in the second terminal, run:
./run_scenario4_topo.sh

or if the above scripts do not work, do the following:

~/pox/pox.py log.level --DEBUG misc.controller4
sudo mn --custom ~/topology4.py --topo topology4 --mac --controller=remote,ip=127.0.0.1,port=6633


+++++++++++++++++++++++++++++++++
Special Notes or any observations
+++++++++++++++++++++++++++++++++
[Any special notes or observations that we need to take care while evaluating scenario 4]
Null
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
							Bonus Scenario
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[List of files that are to be used to execute Bonus Scenario]

++++++++++++++++++++++
Location to copy files
++++++++++++++++++++++
<file_name> - <Location to copy>
[Destination to be provided for each file that is relevant to Bonus Scenario]
of_tutorial.py - /home/mininet/pox/pox/misc/of_tutorial.py
run_scenario5_control.sh - /home/mininet/run_scenario5_control.sh
run_scenario5_topo.sh - /home/mininet/run_scenario5_topo.sh
++++++++++++++++
Commands to Run:
++++++++++++++++
[Any special instructions we need to follow before running commands you will mention below for Bonus Scenario]
make sure that execute the command "./run_scenario5_control.sh" before the command "./run_scenario5_topo.sh"
[List of commands to run before we execute the test cases of Bonus Scenario]
open two SSH terminal for Mininet, in the first terminal, run:
./run_scenario5_control.sh
in the second terminal, run:
./run_scenario5_topo.sh

or if the above scripts do not work, do the following:

~/pox/pox.py log.level --DEBUG misc.controller5
sudo mn --custom ~/topology5.py --topo topology5 --mac --controller=remote,ip=127.0.0.1,port=6633


+++++++++++++++++++++++++++++++++
Special Notes or any observations
+++++++++++++++++++++++++++++++++
[Any special notes or observations that we need to take care while evaluating Bonus Scenario]
The port we specified is 5000. So use iperf -s -p 5000, iperf -c xxxxxxx -p 5000