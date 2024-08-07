#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.log import setLogLevel, info

class SingleSwitchTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        host1 = self.addHost('h1', ip='10.0.0.1/24')
        host2 = self.addHost('h2', ip='10.0.0.2/24')
        host3 = self.addHost('h3', ip='10.0.0.3/24')

        self.addLink(host1, switch)
        self.addLink(host2, switch)
        self.addLink(host3, switch)

if __name__ == '__main__':
    setLogLevel('info')

    topo = SingleSwitchTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)

    net.start()
    info('*** Running ping test\n')
    net.pingAll()
    net.stop()
