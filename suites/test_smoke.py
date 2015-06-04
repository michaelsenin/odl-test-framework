from testtools import TestCase
from libraries import RequestsLibrary
from libraries import SimpleTwoPathTopoExp


import SSHLibrary
import Collections
from libraries import OdlWrapperApi
import time
import nose
from pprint import pprint as pp
import test


requests = RequestsLibrary.RequestsLibrary()
mininet = SimpleTwoPathTopoExp.SimpleTwoPathTopoExp()
odl = OdlWrapperApi.OdlWrapperApi(user='admin', password='admin')

class SmokeTests(TestCase):

    def setUp(self):
        super(SmokeTests, self).setUp()
        mini = mininet.run_mininet('s1:h1,s1:s2,s2:s3,s3:h2')
        self.for_config_delete = '{"marker": "3q3wDQ==","period": 5,"timeout": 15,"switch-policies": []}'
        self.discovery_config = '{"marker": "3q3wDQ==","period": 5,"timeout": 15,"switch-policies": [{"switch-id": "0000000000000001", "policy": "allow-all"},{"switch-id": "0000000000000002", "policy": "allow-all"},{"switch-id": "0000000000000003", "policy": "allow-all"}]}'

    @test.attr("smoke")
    def test_port_statistic(self):
        resp = odl.create_discovery_config(data=self.discovery_config, alias='session')
        self.assertEqual(204, resp.status_code)
        time.sleep(15)
        resp = odl.get_port_statictic(switch_id='0000000000000002', port_id='2', interval='10', alias='session')
        self.assertEqual(204, resp.status_code)

    @test.attr("smoke")
    def test_circuit_creation(self):
        pass

    @test.attr("smoke")
    def test_circuit_statistic(self):
        pass

    @test.attr("smoke")
    def test_port_statistic_from_incorrect_port(self):
        pass

    @test.attr("smoke")
    def test_circuit_on_the_same_switch(self):
        pass

    @test.attr("smoke")
    def test_switch_reachability(self):
        pass

    @test.attr("smoke")
    def test_get_user_list(self):
        pass

    def tearDown(self):
        super(SmokeTests, self).tearDown()
        resp = odl.delete_discovery_config(data=self.for_config_delete, alias='session')
        # assert resp.status == 200
        mininet.stop_mininet()
