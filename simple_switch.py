from ryu.base import app_manager
from ryu.controller import controller
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.event import EventSwitchEnter, EventSwitchLeave
from ryu.lib.packet import ethernet
from ryu.ofproto import ofproto_v1_3

class SimpleController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleController, self).__init__(*args, **kwargs)

    @set_ev_cls(EventSwitchEnter, MAIN_DISPATCHER)
    def switch_enter_handler(self, ev):
        self.logger.info('Switch %s has entered', ev.switch.dp.id)
        self.add_flow(ev.switch.dp)

    @set_ev_cls(EventSwitchLeave, MAIN_DISPATCHER)
    def switch_leave_handler(self, ev):
        self.logger.info('Switch %s has left', ev.switch.dp.id)

    def add_flow(self, dp):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        instructions = [parser.OFPInstructionActions(ofproto.OFPR_ACTIONS, actions)]

        request = parser.OFPFlowMod(
            datapath=dp,
            priority=1,
            match=match,
            instructions=instructions
        )
        dp.send_msg(request)
