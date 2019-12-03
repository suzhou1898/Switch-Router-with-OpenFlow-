'''
of && (of.type != 3) && (of.type != 2)

'''
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr, EthAddr
import struct


log = core.getLogger()


class Tutorial (object):
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    self.my_port_to_ip = [IPAddr("10.0.1.1"), IPAddr("10.0.2.1"), IPAddr("10.0.3.1")]
    self.my_port_to_mac = [
      EthAddr("ff:ff:ff:ff:00:01"),
      EthAddr("ff:ff:ff:ff:00:02"),
      EthAddr("ff:ff:ff:ff:00:03")
    ]    
    self.port_list = [None] * 4
    for i in range(1,4):
      a = self.MyPort(port=i, ip=self.my_port_to_ip[i-1], mac=self.my_port_to_mac[i-1])
      self.port_list[i] = a

    self.mac_to_port = {} # useless
    self.ip_to_port = {}
    self.ip_to_port[IPAddr("10.0.1.100")] = 1
    self.ip_to_port[IPAddr("10.0.2.100")] = 2
    self.ip_to_port[IPAddr("10.0.3.100")] = 3

    self.arp_cache = self.MyDoubleLinkedList()
    self.ip_to_mac = {}

  class MyPort():
    def __init__(self, port, ip, mac):
      self.port = port
      self.ip = ip
      self.mac = mac
      self.net_id = None

  class MyDoubleLinkedList():
    def __init__(self):
      self.anchor = self.node(None)
      self.anchor.next = self.anchor
      self.anchor.prev = self.anchor

    class node():
      def __init__(self, packet):
        self.value = packet
        self.prev = None
        self.next = None

    def add(self, packet):
      new_node = self.node(packet)
      tmp = self.anchor
      while(tmp.next != self.anchor):
        tmp = tmp.next
      new_node.prev = tmp
      new_node.next = tmp.next
      tmp.next.prev = new_node
      tmp.next = new_node

    def pop(self, node):
      node.prev.next = node.next
      node.next.prev = node.prev
      return node

    def find_and_dequeue(self, ip):
      # pop packets with given dst_ip
      # rtr: list[arp packets]
      rst = []
      tmp = self.anchor.next
      while tmp != self.anchor:
        if tmp.value.dstip == ip:
          a = tmp
          b = self.pop(a)
          rst.append(b.value)
          tmp = a.next
        else:
          tmp = tmp.next
      return rst

    def show(self):
      log.debug("ARP cache: ")
      tmp = self.anchor.next
      i = 0
      while tmp != self.anchor:
        log.debug(tmp.value)
        tmp = tmp.next
        i += 1
      log.debug("ARP cache: {0} items".format(i))

    

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    log.debug("--------------------Event arised--------------------")
    packet = event.parsed # This is the parsed packet data.
    log.debug(packet)
    inport = event.port

    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    p_n = packet.next

    self.mac_to_port[packet.src] = inport

    if isinstance(p_n, arp):
      # ARP
      self.ip_to_port[p_n.protosrc] = inport
      self._handle_ARP(packet, p_n, inport)

    elif isinstance(p_n, ipv4):
      # ip
      self.ip_to_port[p_n.srcip] = inport
      self._handle_IP(packet, packet.payload, inport)

  def _handle_IP(self, org_packet, IP_packet, inport):
    log.debug("IP packet received from port {0}".format(inport))
    log.debug("Packet: {0}".format(IP_packet))

    # fm = of.ofp_flow_mod()
    # fm.match.dl_type = 0x0800
    # fm.match.nw_dst = IP_packet.srcip
    # fm.actions.append(of.ofp_action_dl_addr.set_src(self.port_list[inport].mac))
    # fm.actions.append(of.ofp_action_dl_addr.set_dst(org_packet.src))
    # fm.actions.append(of.ofp_action_output(port=inport))
    # self.connection.send(fm)

    if isinstance(IP_packet.payload, icmp):
      # icmp
      log.debug("IP-ICMP_packet: {0}".format(IP_packet))
      self._handle_ICMP(IP_packet, inport, org_packet)

    else:
      # others
      log.debug("IP packet: {0}".format(IP_packet))
      self._transfer_packet(org_packet.payload)
    pass

  def _transfer_packet(self, IP_packet):
    # ethernet packet(frame)
    outport = self.ip_to_port[IP_packet.dstip]
    self.arp_cache.add(IP_packet)
    arp_rq = self._create_arp_packet(arp.REQUEST, EthAddr("ff:ff:ff:ff:ff:ff"), IP_packet.dstip, outport)
    self._send_frame(arp_rq, ethernet.ARP_TYPE, self.port_list[outport].mac, EthAddr("ff:ff:ff:ff:ff:ff"), outport)

  def _handle_ICMP(self, IP_packet, inport, org_packet):
    if IP_packet.payload.type == pkt.TYPE_ECHO_REQUEST:
      log.debug("A ICMP REQUEST packet")

      dst_ip = IP_packet.dstip
      # find dst_ip in routing table
      if dst_ip in self.my_port_to_ip:
        # to one of switch port
        log.debug("not ")

        p = icmp()
        p.type = pkt.TYPE_ECHO_REPLY
        p.payload = IP_packet.payload.payload
        IP_packet.srcip, IP_packet.dstip = IP_packet.dstip, IP_packet.srcip
        IP_packet.payload = p
        self._send_frame(IP_packet, ethernet.IP_TYPE, self.port_list[inport].mac, org_packet.src, inport)
        pass

      elif dst_ip not in self.ip_to_port:
        # unreachable
        log.debug("The ip address {0} is not reachable".format(dst_ip))
        p = self._create_icmp_unreachable(IP_packet, inport)
        self._send_frame(p, ethernet.IP_TYPE, self.port_list[inport].mac, org_packet.src, inport)

      else:
        outport = self.ip_to_port[dst_ip]
        # ip packet enqueue/list? with identifier?: dst_ip
        self.arp_cache.add(IP_packet)
        # send arp request to that port
        arp_rq = self._create_arp_packet(arp.REQUEST, EthAddr("ff:ff:ff:ff:ff:ff"), dst_ip, outport)
        self._send_frame(arp_rq, ethernet.ARP_TYPE, self.port_list[outport].mac, EthAddr("ff:ff:ff:ff:ff:ff"), outport)

    elif IP_packet.payload.type == pkt.TYPE_ECHO_REPLY:
      log.debug("A ICMP REPLY packet")
      log.debug(IP_packet)

      out_port = self.ip_to_port[IP_packet.dstip]
      log.debug(self.ip_to_mac)
      dst_mac = self.ip_to_mac[IP_packet.dstip]
      self._send_frame(IP_packet, ethernet.IP_TYPE, self.port_list[out_port].mac, dst_mac, out_port)

    pass

  def _handle_ARP(self, packet, p_n, inport):
    log.debug("ARP packet received from port {0}".format(inport))
    log.debug("ARP packet: {0}".format(p_n))

    # flow mode
    fm = of.ofp_flow_mod()
    fm.match.dl_type = 0x0800
    fm.match.nw_dst = p_n.protosrc
    fm.actions.append(of.ofp_action_dl_addr.set_src(self.port_list[inport].mac))
    fm.actions.append(of.ofp_action_dl_addr.set_dst(packet.src))
    fm.actions.append(of.ofp_action_output(port=inport))
    self.connection.send(fm)

    # check dst ip addr
    log.debug("ARP dst: {0}".format(p_n.protodst))
    if p_n.protodst not in self.my_port_to_ip:
      log.debug("ARP dst not for me")
      return 0
    
    if p_n.opcode == p_n.REQUEST:
      # ARP request
      log.debug("ARP request: {0}".format(p_n.protodst))
      self.ip_to_mac[p_n.protosrc] = p_n.hwsrc
      # create ARP reply
      return_packet = self._create_arp_packet(arp.REPLY, p_n.hwsrc, p_n.protosrc, inport)
      self._send_frame(return_packet, ethernet.ARP_TYPE, self.port_list[inport].mac, p_n.hwsrc, inport)

      # flow mode
      # fm = of.ofp_flow_mod()
      # fm.match.nw_dst = p_n.protodst
      # fm.match.nw_proto = arp.REQUEST
      # fm.actions.append(of.ofp_action_dl_addr.set_src(self.port_list[inport].mac))
      # fm.actions.append(of.ofp_action_dl_addr.set_dst(p_n.hwsrc))
      # fm.actions.append(of.ofp_action_nw_addr.set_src(self.port_list[inport].ip))
      # fm.actions.append(of.ofp_action_nw_addr.set_dst(p_n.protodst))
      # fm.actions.append(of.ofp_action_)
      pass

    elif p_n.opcode == p_n.REPLY:
      log.debug("APR reply: from {0} to {1}".format(p_n.protosrc, p_n.protodst))

      self.ip_to_mac[p_n.protosrc] = packet.src

      # find src ip
      src_ip = p_n.protosrc
      src_mac = p_n.hwsrc

      # find all pending packets
      # IP packets
      pendings = self.arp_cache.find_and_dequeue(src_ip)

      # send them all
      for ip_packet in pendings:
        self._send_frame(ip_packet, ethernet.IP_TYPE, self.port_list[inport].mac, p_n.hwsrc, inport)
        pass   
    pass

  def _create_arp_packet(self, opcode, dst_mac, dst_ip, outport):
    p = arp()
    p.opcode = opcode
    p.hwsrc = self.port_list[outport].mac
    p.hwdst = dst_mac
    p.protosrc = self.port_list[outport].ip
    p.protodst = dst_ip
    return p

  def _create_icmp_unreachable(self, ip_packet, inport):
    p = icmp()
    p.type = pkt.TYPE_DEST_UNREACH
    data = ip_packet.pack()
    data = data[:ip_packet.hl * 4 + 8]
    data = struct.pack("!HH", 0, 0) + data
    p.payload = data

    p_ip = ipv4()
    p_ip.protocol = p_ip.ICMP_PROTOCOL
    p_ip.srcip = self.port_list[inport].ip
    p_ip.dstip = ip_packet.srcip

    p_ip.payload = p
    return p_ip
  
  def _send_frame(self, packet, frame_type, src, dst, outport):
    log.debug("Sending packet: src: {0}, dst: {1}, to port {2}".format(src, dst, outport))
    e = ethernet()
    e.type = frame_type
    e.src = src
    e.dst = dst
    e.payload = packet
    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
    msg.in_port = outport
    self.connection.send(msg)


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)


