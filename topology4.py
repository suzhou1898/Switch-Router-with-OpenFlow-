'''
sudo mn --custom topology4.py --topo topology4 --mac --controller=remote,ip=127.0.0.1,port=6633
'''
from mininet.topo import Topo

class s4_Topo( Topo ):

    def __init__( self ):
        "Create custom topo."
        # Initialize topology
        Topo.__init__( self )

		#Add hosts and switches
        host4 = self.addHost( 'h4', ip="10.0.1.2/24", defaultRoute = "via 10.0.1.1" )
        host5 = self.addHost( 'h5', ip="10.0.1.3/24", defaultRoute = "via 10.0.1.1" )
        host6 = self.addHost( 'h6', ip="10.0.1.4/24", defaultRoute = "via 10.0.1.1" )

        host7 = self.addHost( 'h7', ip="10.0.2.2/24", defaultRoute = "via 10.0.2.1" )
        host8 = self.addHost( 'h8', ip="10.0.2.3/24", defaultRoute = "via 10.0.2.1" )
        host9 = self.addHost( 'h9', ip="10.0.2.4/24", defaultRoute = "via 10.0.2.1" )

        host10 = self.addHost( 'h10', ip="10.0.3.2/24", defaultRoute = "via 10.0.3.1" )
        host11 = self.addHost( 'h11', ip="10.0.3.3/24", defaultRoute = "via 10.0.3.1" )
        host12 = self.addHost( 'h12', ip="10.0.3.4/24", defaultRoute = "via 10.0.3.1" )
        
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')

		#Add links
        self.addLink(host4, switch1, port1=1, port2=2)
        self.addLink(host5, switch1, port1=1, port2=3)
        self.addLink(host6, switch1, port1=1, port2=4)

        self.addLink(host7, switch2, port1=1, port2=2)
        self.addLink(host8, switch2, port1=1, port2=3)
        self.addLink(host9, switch2, port1=1, port2=4)

        self.addLink(host10, switch3, port1=1, port2=2)
        self.addLink(host11, switch3, port1=1, port2=3)
        self.addLink(host12, switch3, port1=1, port2=4)

        self.addLink(switch1, switch2, port1=1, port2=1)
        self.addLink(switch2, switch3, port1=5, port2=5)
        self.addLink(switch1, switch3, port1=6, port2=6)
	
topos = { 'topology4': (lambda: s4_Topo() ) }
