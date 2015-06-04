import json

from RequestsLibrary import RequestsLibrary
from robot.libraries.BuiltIn import BuiltIn

builtin = BuiltIn()

API = {
    'create_discovery_config': '/controller/nb/v2/ncn/lldp-discovery',
    'delete_discovery_config': '/controller/nb/v2/ncn/lldp-discovery',
    'create_circuit': '/controller/nb/v2/ncn/circuits',
    'delete_circuit': '/controller/nb/v2/ncn/circuits',
    'get_port_statictic': 'controller/nb/v2/ncn/statistics/switches',
    'get_circuit_statistic': 'controller/nb/v2/ncn/statistics/circuits',
    'get_switch': 'controller/nb/v2/ncn/diagnostics/switches',
    'get_user_list': 'auth/v1/users',
    'get_datapath_validation': 'controller/nb/v2/ncn/datapath-validation',
    'put_datapath_validation': 'controller/nb/v2/ncn/datapath-validation',
    'get_dom_tree': 'restconf/config/ncn-isl:route-container/',
    'get_circuit_path': 'controller/nb/v2/ncn/diagnostics/circuits',
    'get_switch_state': 'controller/nb/v2/ncn/diagnostics/switches',
    'get_diagnostic_circuits': '/controller/nb/v2/ncn/diagnostics/circuits',
    'find_route': '/controller/nb/v2/ncn/diagnostics/keep-alive/find-route',
    'get_diagnostic_switches': '/controller/nb/v2/ncn/diagnostics/switches',
    'get_list_delay_tasks': '/controller/nb/v2/ncn/diagnostics/switches-delay',
    'create_switches_delay_task': '/controller/nb/v2/ncn/diagnostics/switches-delay',
    'get_delay_task': '/controller/nb/v2/ncn/diagnostics/switches-delay',
    'delete_delay_task': '/controller/nb/v2/ncn/diagnostics/switches-delay'
}


def api_wrapper(f):
    def wrapper(*args, **kwargs):
        for arg in kwargs:
            if arg == 'data':
                if isinstance(kwargs[arg], dict):
                    kwargs[arg] = json.dumps(kwargs[arg])
                else:
                    kwargs[arg] = str(kwargs[arg])

                builtin.log('DATA to send: {0}'.format(kwargs[arg]),
                            'DEBUG')
                kwargs['data'] = json.loads(kwargs[arg], strict=False)
            else:
                kwargs[arg] = str(kwargs[arg])

        kwargs['uri'] = API[f.__name__]

        resp = f(*args, **kwargs)
        return resp
    return wrapper


class OdlWrapperApi(RequestsLibrary):

    def __init__(self, user, password, url='http://127.0.0.1:8080',
                 headers={'Content-Type': 'application/json'}):
        self.session = \
            self.create_session(url=url, 
                                auth=[user, password], headers=headers)

    @api_wrapper
    def create_discovery_config(self, data, alias, **kwargs):
        resp = self.put(data=data, alias=alias, **kwargs)
        return resp

    @api_wrapper
    def delete_discovery_config(self, data, alias, **kwargs):
        resp = self.put(data=data, alias=alias, **kwargs)
        return resp

    @api_wrapper
    def create_circuit(self, data, alias, **kwargs):
        resp = self.put(data=data, alias=alias, **kwargs)
        return resp

    @api_wrapper
    def delete_circuit(self, circuit_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], circuit_id])
        resp = self.delete(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_circuit_statistic(self, circuit_id, interval, alias, **kwargs):
        kwargs['uri'] = \
            '/'.join([kwargs['uri'], circuit_id + '?interval=' + interval])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_port_statictic(self, switch_id, port_id, interval,
                           alias, **kwargs):
        uri = \
            [kwargs['uri'], switch_id, 'ports',
             port_id + '?interval=' + interval]
        kwargs['uri'] = '/'.join(uri)
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_switch(self, switch_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], switch_id])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_user_list(self, alias, **kwargs):
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_datapath_validation(self, alias, **kwargs):
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def put_datapath_validation(self, data, alias, **kwargs):
        resp = self.put(data=data, alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_dom_tree(self, alias, **kwargs):
        resp = self.get(alias=alias, **kwargs)
        builtin.log('DOM tree: {0}'.format(str(resp.json())),
                    'DEBUG')
        return resp

    @api_wrapper
    def get_circuit_path(self, circuit_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], circuit_id, 'path'])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_switch_state(self, node_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], node_id])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def find_route(self, switch1, switch2, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], switch1, switch2])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_list_delay_tasks(self, alias, **kwargs):
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def create_switches_delay_task(self, source_switch,
                                   dest_switch, alias,
                                   **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'],
                                 source_switch, dest_switch])
        resp = self.put(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def get_delay_task(self, task_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], task_id])
        resp = self.get(alias=alias, **kwargs)
        return resp

    @api_wrapper
    def delete_delay_task(self, task_id, alias, **kwargs):
        kwargs['uri'] = '/'.join([kwargs['uri'], task_id])
        resp = self.delete(alias=alias, **kwargs)
        return resp
