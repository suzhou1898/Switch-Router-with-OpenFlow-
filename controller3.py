from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.packet.icmp import icmp
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr, EthAddr
import struct
import time

log = core.getLogger()
DEFAULT_GATEWAY = 1
validIP = [IPAddr('10.0.1.1'), IPAddr('10.0.1.2'), IPAddr('10.0.1.3'), IPAddr('10.0.2.1'), IPAddr('10.0.2.2'), IPAddr('10.0.2.3'), IPAddr('10.0.2.4')]
subnet1 = ['10.0.1.1', '10.0.1.2', '10.0.1.3']
subnet2 = ['10.0.2.1', '10.0.2.2', '10.0.2.3', '10.0.2.4']

class router(object):
  def __init__(self):
    log.debug('router registered')
    # The dict for all routers, desginated by dpid
    # In each dict, each component is also a dict indexed by dpid
    self.arpTable = {}
    self.arpWait = {}
    self.routingTable = {}
    self.connections = {}
    self.routerIP = {}
    core.openflow.addListeners(self)

  def _handle_GoingUpEvent(self, event):
    self.listenTo(core.openflow)
    log.debug("Router is up")

  def _handle_ConnectionUp(self, event):
    log.debug("--------------- connection comes: dpid {0} ---------------".format(event.dpid))
    dpid = event.dpid

    log.debug("Generating IP and MAC basing on dpid: ")
    ip = IPAddr('10.0.{0}.1'.format(dpid))
    mac = EthAddr("{:0>12x}".format(event.dpid | 0x0000ffff0000))
    log.debug("IP: {0}, MAC: {1}".format(ip, mac))

    log.debug("Building up tables")
    self.routerIP[dpid] = ip
    if dpid not in self.connections:
        self.connections[dpid] = event.connection
    if dpid not in self.arpTable:
        self.arpTable[dpid] = {}
    if dpid not in self.routingTable:
        self.routingTable[dpid] = {}
    if dpid not in self.arpWait:
        self.arpWait[dpid] = {}
    self.arpTable[dpid][ip] = mac

    # use arp to let routers know each others
    for router in self.routerIP:
      if router != dpid:
        self._handle_ARP_Request(ip, self.routerIP[router], mac, of.OFPP_FLOOD, dpid)

  def _handle_ConnectionDown(self, event):
    log.debug("Connection from router {0} is down, cleaning tables".format(event.dpid))
    if event.dpid in self.arpTable:
        del self.arpTable[event.dpid]
    if event.dpid in self.routingTable:
        del self.routingTable[event.dpid]
    if event.dpid in self.connections:
        del self.connections[event.dpid]
    if event.dpid in self.arpWait:
        del self.arpWait[event.dpid]
    if event.dpid in self.routerIP:
        del self.routerIP[event.dpid]

  def _handle_PacketIn (self, event):
    log.debug("---------------------------event---------------------------")
    packet = event.parsed
    dpid = event.connection.dpid
    inport = event.port
    log.debug("Router {0}: in port {1}, {2}".format(dpid, inport, packet))

    if not packet.parsed:
      log.error("Incomplete packet")
      return

    packetIn = event.ofp
    payload = packet.payload
    log.debug("Router {0}: {1}".format(dpid, payload))

    if isinstance(payload, arp):
      # arp
      self._handle_ARP(payload, inport, dpid, packetIn)

    elif isinstance(payload, ipv4):
      # ip
      log.debug("Router {0}: ipv4 packet in port {1}, from {2} to {3}".format(dpid, inport, packet.next.srcip, packet.next.dstip))

      self._add_IP(payload.srcip, dpid, inport)

      if payload.dstip not in validIP:
        self._handle_ICMP_Reply(dpid, packet, payload.srcip, payload.dstip, pkt.TYPE_DEST_UNREACH)
        return
      
      if payload.dstip == self.routerIP[dpid]:
        # payload for you, should be an icmp request
        if isinstance(payload.next, icmp):
          log.debug("Router {0}: ICMP packet comes to router".format(dpid))
          self._handle_ICMP_Reply(dpid, packet, payload.srcip, payload.dstip, pkt.TYPE_ECHO_REPLY)
      
      elif (payload.dstip in subnet1 and self.routerIP[dpid] in subnet2) or (payload.dstip in subnet2 and self.routerIP[dpid] in subnet1):
        #different subnet
        nextIP = IPAddr('10.0.{0}.1'.format(3-dpid))
        nextMac = self.arpTable[dpid][nextIP]
        msg = of.ofp_packet_out(buffer_id=packetIn.buffer_id, in_port=inport)
        msg.actions.append(of.ofp_action_dl_addr.set_dst(nextMac))
        msg.actions.append(of.ofp_action_output(port=1))# FIXED router to router port
        self.connections[dpid].send(msg)
        log.debug('Router {0}: packet from {1} to {2}, is in different subnet, send to port 1'.format(dpid, payload.srcip, payload.dstip))

        # install flow
        fm = of.ofp_flow_mod()
        fm.match.dl_type = 0x800
        fm.match.nw_dst = payload.dstip
        fm.actions.append(of.ofp_action_dl_addr.set_dst(nextMac))
        fm.actions.append(of.ofp_action_output(port=1))
        self.connections[dpid].send(fm)
      
      else:
        #same subnet
        if payload.dstip not in self.routingTable[dpid] or payload.dstip not in self.arpTable[dpid]:
          log.debug("Router {0}, packet from {1} to {2}, unknown destination, adding to arpWait".format(dpid, payload.srcip, payload.dstip))
          # create a list of pending packet, check if any
          if payload.dstip not in self.arpWait[dpid]:
            self.arpWait[dpid][payload.dstip] = []

          entry = (packetIn.buffer_id, inport)
          self.arpWait[dpid][payload.dstip].append(entry)
          self._handle_ARP_Request(payload.srcip, payload.dstip, packet.src, inport, dpid)
        else:
          msg = of.ofp_packet_out(buffer_id=packetIn.buffer_id, in_port=inport)
          msg.actions.append(of.ofp_action_dl_addr.set_dst(self.arpTable[dpid][payload.dstip]))
          msg.actions.append(of.ofp_action_output(port=self.routingTable[dpid][payload.dstip]))
          self.connections[dpid].send(msg)
          log.debug('Router {0}: packet from {1} to {2}, same subnet, sending to port {3}'.format(dpid, payload.srcip, payload.dstip, self.routingTable[dpid][payload.dstip]))

          # install flow
          msg = of.ofp_flow_mod()
          msg.match.dl_type = 0x800
          msg.match.nw_dst = payload.dstip
          msg.actions.append(of.ofp_action_dl_addr.set_dst(self.arpTable[dpid][payload.dstip]))
          msg.actions.append(of.ofp_action_output(port=self.routingTable[dpid][payload.dstip]))
          self.connections[dpid].send(msg)

  def _send_packet(self, dpid, packetIn, outPort):
    msg = of.ofp_packet_out()
    msg.data = packetIn
    action = of.ofp_action_output(port=outPort)
    msg.actions.append(action)
    self.connections[dpid].send(msg)

  def _handle_ARP(self, ARP_packet, inport, dpid, packetIn):
    # learn ip routing table
    self._add_IP(ARP_packet.protosrc, dpid, inport)

    log.debug("Router {0}: ARP packet in port {1}, from {2} to {3}".format(dpid, inport, ARP_packet.protosrc, ARP_packet.protodst))

    # learn arp table
    if ARP_packet.protosrc not in self.arpTable[dpid]:
      log.debug("Router {0}: adding {1} - {2} to  ARP table".format(dpid, ARP_packet.protosrc, ARP_packet.hwsrc))
      self.arpTable[dpid][ARP_packet.protosrc] = ARP_packet.hwsrc
      
      # send all pending packets
      if ARP_packet.protosrc in self.arpWait[dpid] and (len(self.arpWait[dpid][ARP_packet.protosrc]) > 0):
        self._handle_ARP_Wait(ARP_packet.protosrc, dpid)

    if ARP_packet.opcode == arp.REQUEST:
      # log.debug("Router {0}: ARP Request".format(dpid))
      if ARP_packet.protodst == self.routerIP[dpid]:
        log.debug("Router {0}: ARP Request  for me, replying".format(dpid))
        self._handle_ARP_Reply(ARP_packet, inport, dpid)
      else:
        log.debug("Router {0}: ARP Request, not for me, flooding".format(dpid))
        self._send_packet(dpid, packetIn, of.OFPP_FLOOD)

    elif ARP_packet.opcode == arp.REPLY and ARP_packet.protodst != IPAddr('10.0.{0}.1'.format(dpid)):
      # if packet is for me, I need to send all pending packets, which
      # has been done
      log.debug("Router {0}: ARP Reply, retransmitting to port {1}".format(dpid, self.routingTable[dpid][ARP_packet.protodst]))
      self._send_packet(dpid, packetIn, self.routingTable[dpid][ARP_packet.protodst])

  def _handle_ARP_Wait(self, src_ip, dpid):
    log.debug("Router {0}: Sending all pending packets for IP {1}".format(dpid, src_ip))
    log.debug("Router {0}: pending packets: ".format(dpid, self.arpWait[dpid][src_ip]))
    # send all pending packets
    while len(self.arpWait[dpid][src_ip]) > 0:
      (bid, inport) = self.arpWait[dpid][src_ip][0]
      msg = of.ofp_packet_out(buffer_id = bid, in_port = inport)
      msg.actions.append(of.ofp_action_dl_addr.set_dst(self.arpTable[dpid][src_ip]))
      msg.actions.append(of.ofp_action_output(port = self.routingTable[dpid][src_ip]))
      self.connections[dpid].send(msg)
      log.debug("Router {0}: send wait ARP packet, destIP: {1}, destMAC: {2}, output port: {3}".format(dpid, src_ip, self.arpTable[dpid][src_ip], self.routingTable[dpid][src_ip]))
      del self.arpWait[dpid][src_ip][0]
      pass

  def _handle_ARP_Reply(self, ARP_packet, inport, dpid):
    tmp = arp()  # t is routing, a is ARP
    tmp.hwtype = ARP_packet.hwtype
    tmp.prototype = ARP_packet.prototype
    tmp.hwlen = ARP_packet.hwlen
    tmp.protolen = ARP_packet.protolen
    tmp.opcode = arp.REPLY
    tmp.hwdst = ARP_packet.hwsrc
    tmp.protodst = ARP_packet.protosrc
    tmp.protosrc = ARP_packet.protodst
    tmp.hwsrc = self.arpTable[dpid][ARP_packet.protodst]

    e = ethernet(type=ethernet.ARP_TYPE, src=self.arpTable[dpid][ARP_packet.protodst], dst=ARP_packet.hwsrc)
    e.set_payload(tmp)

    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
    msg.in_port = inport
    log.debug("Router {0}: sending ARP reply from {1} to  {2} in port {3}".format(dpid, ARP_packet.protodst, tmp.protodst, inport))

    self.connections[dpid].send(msg)

  def _handle_ARP_Request(self, src_ip, dst_ip, src_mac, inport, dpid):
    arp_packet = arp()
    arp_packet.hwtype = arp_packet.HW_TYPE_ETHERNET
    arp_packet.prototype = arp_packet.PROTO_TYPE_IP
    arp_packet.hwlen = 6
    arp_packet.protolen = arp_packet.protolen
    arp_packet.opcode = arp_packet.REQUEST
    arp_packet.hwdst = ETHER_BROADCAST
    arp_packet.protodst = dst_ip
    arp_packet.hwsrc = src_mac
    arp_packet.protosrc = src_ip

    e = ethernet(type=ethernet.ARP_TYPE, src=src_mac, dst=ETHER_BROADCAST)
    e.set_payload(arp_packet)

    log.debug("Router {0}: sending ARP request from {1} to {2} inport {3}".format(dpid, str(src_ip), dst_ip, inport))

    msg = of.ofp_packet_out()
    msg.data = e.pack()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    self.connections[dpid].send(msg)

  def _handle_ICMP_Reply(self, dpid, ethernet_packet, srcip, dstip, icmpType):
    ICMP_packet = icmp()
    ICMP_packet.type = icmpType
    if icmpType == pkt.TYPE_ECHO_REPLY:
      ICMP_packet.payload = ethernet_packet.find('icmp').payload
    elif icmpType == pkt.TYPE_DEST_UNREACH:
      oriIp = ethernet_packet.find('ipv4')
      d = oriIp.pack()
      d = d[:oriIp.hl * 4 + 8]
      d = struct.pack("!HH", 0, 0) + d
      ICMP_packet.payload = d

    IP_packet = ipv4()
    IP_packet.protocol = IP_packet.ICMP_PROTOCOL
    IP_packet.srcip = dstip
    IP_packet.dstip = srcip
    IP_packet.payload = ICMP_packet

    e = ethernet()
    e.src = ethernet_packet.dst
    if (srcip in subnet1 and self.routerIP[dpid] in subnet1) or (srcip in subnet2 and self.routerIP[dpid] in subnet2):
        e.dst = ethernet_packet.src
    else:
        gatewayIP = IPAddr('10.0.%d.1' % (3-dpid))
        e.dst = self.arpTable[dpid][gatewayIP]
    e.type = e.IP_TYPE
    e.payload = IP_packet

    msg = of.ofp_packet_out()
    msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
    msg.data = e.pack()
    msg.in_port = self.routingTable[dpid][srcip]
    self.connections[dpid].send(msg)
    log.debug("Router {0}: {1} ping router at {2}".format(dpid, srcip, dstip))

  def _add_IP(self, ip, dpid, inport):
    if ip not in self.routingTable[dpid]:
      log.debug("Router {0}: adding IP {1} to routing table, port {2}".format(dpid, ip, inport))
      self.routingTable[dpid][ip] = inport

def launch():
    core.registerNew(router)