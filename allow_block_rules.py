from ryu.base import app_manager
from ryu.controller import controller
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.ofproto import ofproto_v1_3

class SimpleFirewall(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleFirewall, self).__init__(*args, **kwargs)
        self.allow_ip = '10.0.0.1'  # Adjust based on Mininet IPs
        self.block_ip = '10.0.0.2'  # Adjust based on Mininet IPs

    @set_ev_cls(CONFIG_DISPATCHER)
    def on_config(self, event):
        # Store the datapath instance
        datapath = event.datapath
        self._install_flow_rules(datapath)

    def _install_flow_rules(self, datapath):
        self._add_flow(datapath, self.allow_ip, allow=True)
        self._add_flow(datapath, self.block_ip, allow=False)

    def _add_flow(self, datapath, ip, allow):
        ofproto = datapath.ofproto
        parser = datapath.parser

        # Create match criteria
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip)
        
        # Create actions
        if allow:
            actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        else:
            actions = []

        # Create flow entry
        inst = [parser.OFPInstructionActions(ofproto.OFPR_ACTIONS, actions)]
        self.add_flow(datapath, 1, match, inst)

    def add_flow(self, datapath, priority, match, instructions):
        ofproto = datapath.ofproto
        parser = datapath.parser

        actions = instructions
        inst = [parser.OFPInstructionActions(ofproto.OFPR_ACTIONS, actions)]
        request = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst
        )
        datapath.send_msg(request)

    @set_ev_cls(MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip = pkt.get_protocol(ipv4.ipv4)

        if ip:
            self.logger.info(f'Packet-in from IP: {ip.src}')

            # Check if the IP should be allowed or blocked
            if ip.src == self.block_ip:
                self.logger.info(f'Blocking packet from IP: {ip.src}')
                # Create drop flow rule to block traffic
                match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip.src)
                actions = []
                self.add_flow(datapath, 1, match, actions)
            elif ip.src == self.allow_ip:
                self.logger.info(f'Allowing packet from IP: {ip.src}')
                # Allow traffic by installing a flow rule with normal action
                match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip.src)
                actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
                self.add_flow(datapath, 1, match, actions)
