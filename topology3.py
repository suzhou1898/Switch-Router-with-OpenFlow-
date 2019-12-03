'''
sudo mn --custom topology3.py --topo topology3 --mac --controller=remote,ip=127.0.0.1,port=6633
'''
from mininet.topo import Topo

class s3_Topo( Topo ):

    def __init__( self ):
        "Create custom topo."
        # Initialize topology
        Topo.__init__( self )

		#Add hosts and switches
        host3 = self.addHost( 'h3', ip="10.0.1.2/24", defaultRoute = "via 10.0.1.1" )
        host4 = self.addHost( 'h4', ip="10.0.1.3/24", defaultRoute = "via 10.0.1.1" )
        host5 = self.addHost( 'h5', ip="10.0.2.2/24", defaultRoute = "via 10.0.2.1" )
        
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

		#Add links
        self.addLink(host3, switch1, port1=1, port2=2)
        self.addLink(host4, switch1, port1=1, port2=3)
        self.addLink(host5, switch2, port1=1, port2=2)
        self.addLink(switch1, switch2, port1=1, port2=1)
	
topos = { 'topology3': (lambda: s3_Topo() ) }
