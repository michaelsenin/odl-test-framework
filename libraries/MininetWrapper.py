"""
Create custom mininet topology and delete it
"""
import re
import itertools
import collections

from time import sleep

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.clean import cleanup
from mininet import node
from robot.libraries.BuiltIn import BuiltIn


builtin = BuiltIn()


def user_switch(name, **kwargs):
    kwargs['datapath'] = 'user'
    kwargs['protocols'] = 'OpenFlow13'
    return node.OVSSwitch(name, **kwargs)


def remote_controller(name, **kwargs):
    kwargs['ip'] = '127.0.0.1'
    return node.RemoteController(name, **kwargs)


class MininetWrapper(object):

    def __init__(self):
        self.mininet_client = None
        self.topology = []
        self.delay = None

    def set_delay(self, delay):
        delay = str(int(delay)) + 'ms'
        self.delay = delay

    def run_mininet(self, topology_string):
        """ Create and run multiple link network
        """
        self.topo_client = Topo()
        hosts = set()
        switches = set()

        relations = re.sub(r's', '', topology_string)
        relations = [i.split(':') for i in relations.split(',')
                     if 'h' not in i]
        relations = [[int(y) - 1 for y in x] for x in relations]
        builtin.log(relations, 'DEBUG')

        verticles_count = len(set(list(itertools.chain(*relations))))
        builtin.log(self.topology, 'DEBUG')

        for i in xrange(verticles_count):
            temp = []
            for j in xrange(verticles_count):
                temp.append(-1)
            self.topology.append(temp[:])

        builtin.log(self.topology, 'DEBUG')

        for i in relations:
            self.topology[i[0]][i[1]] = 1
            self.topology[i[1]][i[0]] = 1
        builtin.log(self.topology, 'DEBUG')

        for v1, v2 in [x.split(':') for x in str(topology_string).split(',')]:
            if 'h' in v1 and v1 not in hosts:
                self.topo_client.addHost(v1)
                hosts.add(v1)
            if 'h' in v2 and v2 not in hosts:
                self.topo_client.addHost(v2)
                hosts.add(v2)
            if 's' in v1 and v1 not in switches:
                self.topo_client.addSwitch(v1)
                switches.add(v1)
            if 's' in v2 and v2 not in switches:
                self.topo_client.addSwitch(v2)
                switches.add(v2)
            if self.delay:
                self.topo_client.addLink(v1, v2, delay=self.delay)
            else:
                self.topo_client.addLink(v1, v2)

        self.mininet_client = Mininet(switch=user_switch,
                                      controller=remote_controller,
                                      topo=self.topo_client, link=TCLink)
        self.mininet_client.start()
        builtin.log('Links info:')
        for link in self.topo_client.links(withKeys=True, withInfo=True):
            builtin.log(link)

        # self.mininet_client.waitConnected(timeout=20)
        sleep(20)

    def stop_mininet(self):
        if self.mininet_client is not None:
            self.mininet_client.stop()
        if self.topology:
            self.topology = []
        self.delay = None
        cleanup()
        sleep(20)

    def kill_link(self, host1, host2):
        host1, host2 = str(host1), str(host2)
        self.mininet_client.configLinkStatus(host1, host2, 'down')

        if 'h' not in host1 and 'h' not in host2:
            num_1 = int(host1[1:]) - 1
            num_2 = int(host2[1:]) - 1
            self.topology[num_1][num_2] = -1
            self.topology[num_2][num_1] = -1

        builtin.log(self.topology, 'DEBUG')
        builtin.log('Down link {0} - {1}'.format(host1, host2),
                    'DEBUG')

    def check_link(self, host1, host2):
        switch = self.mininet_client.getNodeByName(host1)
        connections = switch.connectionsTo(host2)
        if connections:
            return True
        else:
            return False

    def up_link(self, host1, host2):
        host1, host2 = str(host1), str(host2)
        self.mininet_client.configLinkStatus(host1, host2, 'up')
        if 'h' not in host1 and 'h' not in host2:
            num_1 = int(host1[1:]) - 1
            num_2 = int(host2[1:]) - 1
            self.topology[num_1][num_2] = 1
            self.topology[num_2][num_1] = 1
        builtin.log(self.topology, 'DEBUG')
        builtin.log('Up link {0} - {1}'.format(host1, host2),
                    'DEBUG')

    def stop_node(self, name):
        node = self.mininet_client.getNodeByName(name)
        node.stop()
        num_node = int(name[1:]) - 1
        self.topology[num_node][num_node] = -1
        builtin.log('Node {0} was stoped'.format(name),
                    'DEBUG')

    def check_connected_node(self, name):
        switch = self.mininet_client.getNodeByName(name)
        return switch.connected()

    # NOTE(msenin) unstable method - after stoping mininet cant start node
    # mininet doesn't return exception
    def start_node(self, name):
        node = self.mininet_client.getNodeByName(name)
        # TODO (msenin) add option controller_name
        controllers = self.mininet_client.controllers
        builtin.log('Controllers: {0}'.format(controllers),
                    'DEBUG')
        node.start([controllers[0]])

    def check_rules(self):
        switches = self.mininet_client.switches
        results = []
        regex = (r'(cookie=[\w\d]+),|(dl_dst=[\w\d:\/]{35})'
                 '|(priority=[\d]+),|(dl_src=[\w\d:\/]{17})')

        for switch in switches:
            ans = switch.dpctl('dump-flows -O OpenFlow13')
            builtin.log(
                'Rules on the switch {0}: {1}'.format(switch.name, ans),
                'DEBUG')

            ans_with_regex = ""
            for m in re.finditer(regex, ans):
                for i in xrange(1, 5):
                    if m.group(i):
                        ans_with_regex = ans_with_regex + ', ' + m.group(i)
            builtin.log(
                'Rules with regex {0}: {1}'.format(switch.name, ans),
                'DEBUG')
            results.append({switch.name: ans_with_regex})

        return results

    def compare_dumped_flows(self, rules1, rules2):
        rules_1 = str(rules1)
        rules_2 = str(rules2)

        builtin.log('Compare two flow tables(without changing parts): ',
                    'DEBUG')

        builtin.log(rules_1, 'DEBUG')
        builtin.log(rules_2, 'DEBUG')

        if rules_1 != rules_2:
            return False
        return True

    def ping(self, name1, name2):
        node1 = self.mininet_client.getNodeByName(name1)
        node2 = self.mininet_client.getNodeByName(name2)
        ping = self.mininet_client.ping(hosts=[node1, node2], timeout=10)
        num1, num2 = name1[1:], name2[1:]

        cmd1 = node1.cmd('ifconfig')
        builtin.log('{0}'.format(cmd1), 'DEBUG')
        cmd1 = node1.cmd('ping -d -c 5 -w 5 10.0.0.' + num2)
        builtin.log('{0}'.format(cmd1), 'DEBUG')

        cmd2 = node2.cmd('ifconfig')
        builtin.log('{0}'.format(cmd2), 'DEBUG')
        cmd1 = node2.cmd('ping -d -c 5 -w 5 10.0.0.' + num1)
        builtin.log('{0}'.format(cmd1), 'DEBUG')
        return int(ping)

    def check_route_state(self, route):
        # TODO (msenin) delete method after tests refactoring
        """Check the state of route
        :param route: list with verticles (each verticle is switch id)
        """
        route = map(lambda x: int(x) - 1, route)
        for i in xrange(1, len(route)):
            prev = route[i - 1]
            cur = route[i]
            if (self.topology[prev][prev] == -1 or
                    self.topology[cur][cur] == -1):
                return False
            if self.topology[prev][cur] == -1:
                return False
        return True

    def contains_route_in_routes(self, route, routes):
        builtin.log("route: {0}".format(route), 'DEBUG')
        builtin.log("routes: {0}".format(routes), 'DEBUG')

        route = map(lambda x: int(x), route)
        for i in routes:
            if i.get('route') and map(lambda x: int(x), i['route']) == route:
                return True
        return False

    def parse_tree(self, resp):
        """Define and check the routes and links
        :param resp:json from response
        """
        builtin.log("JSON for parsing: {0}".format(resp), 'DEBUG')
        source_node_list = set()
        destination_node_list = set()
        links_dict = collections.OrderedDict()
        routes = []
        states_dict = dict()
        route_container = resp.get('route-container')
        route_list = route_container.get('route-list')
        route_list_length = len(route_list)
        # TODO
        for i in range(0, route_list_length):
            needed_leaf = i
        route_leaf = route_list[needed_leaf]
        leaf_source = route_leaf.get('source')
        leaf_destination = route_leaf.get('destination')
        states_dict['source'] = leaf_source
        states_dict['destination'] = leaf_destination
        route = route_leaf.get('route', [])
        for i in range(0, len(route)):
            route_state = dict()
            vertexes = set()
            path = route[i]
            state = path.get('state')
            route_state['state'] = state
            route_state['route'] = vertexes
            routes.append(route_state)
            states_dict['routes'] = routes
            links = path.get('path')
            links_count = len(links)
            for j in range(0, links_count):
                link = links[j]
                link_source = link.get('source')
                link_destination = link.get('destination')
                source_node = link_source.get('source-node')
                destination_node = link_destination.get('dest-node')
                source_flow = source_node.split(':')[-1]
                destination_flow = destination_node.split(':')[-1]
                vertexes.add(source_flow)
                vertexes.add(destination_flow)
                source_node_list.add(source_node)
                destination_node_list.add(destination_node)
                links_dict[source_node] = destination_node
        return states_dict

    def parse_tree_2(self, resp):
        """Parse output json from ncn restconfig
        :param resp:json from response
        [{'state': 'up', 'destination': '4',
          'route': ['1', '4'], 'source': '1', 'id': 100},
        ....................................................................
        {'destination': '3', 'source': '1'},
        {'destination': '7', 'source': '1'}]
        """
        builtin.log("JSON for parsing: {0}".format(resp), 'DEBUG')

        routes = []

        route_list = resp.get('route-container').get('route-list')
        for routes_between_switches in route_list:
            routes_rest_conf = routes_between_switches.get("route")
            if routes_rest_conf:
                # NOTE (msenin)
                # format of fields 'source' and 'destination': openflow:4
                for route_rest in routes_rest_conf:
                    route = {}
                    route['source'] = int(route_rest['source'][9:])
                    route['destination'] = \
                        int(route_rest['destination'][9:])
                    route['state'] = route_rest['state']
                    pathes = route_rest.get('path')
                    route['id'] = route_rest.get('id')
                    path = []
                    for link in pathes:
                        link_source = link.get('source')
                        link_destination = link.get('destination')
                        source_node = link_source.get('source-node')
                        destination_node = link_destination.get('dest-node')
                        source_flow = int(source_node[9:])
                        destination_flow = int(destination_node[9:])
                        if source_flow not in path:
                            path.append(source_flow)
                        if destination_flow not in path:
                            path.append(destination_flow)
                    route['route'] = path
                    routes.append(route)
            else:
                route = {}
                route['source'] = int(routes_between_switches['source'][9:])
                route['destination'] = \
                    int(routes_between_switches['destination'][9:])
                routes.append(route)
        return routes

    def check_route_state_by_DOM_tree(self, route, tree):
        """ return 1 if route up, -1 down and 0 if unexist
        """
        if isinstance(route, str) or isinstance(route, unicode):
            route = list(route[1:-1].split(','))
        route = map(lambda x: int(x), route)

        builtin.log("route: {0}".format(route), 'DEBUG')
        tree = self.parse_tree_2(tree)
        builtin.log("tree: {0}".format(tree), 'DEBUG')
        filtered_tree = filter(lambda x: x.get('route') == route, tree)
        if filtered_tree:
            if filtered_tree[0]['state'] == 'up':
                return 1
            else:
                return -1
        else:
            return 0

    def filter_DOM_tree_by_field(self, condition, tree):
        # TODO (msenin) add logger
        tree = self.parse_tree_2(tree)
        filtered_tree = filter(lambda field: eval(condition), tree)
        return filtered_tree
