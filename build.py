from config import Config
from robot.conf import RobotSettings
from time import sleep

import logging
import sys
import docker
from robot import run
from robot.running import TestSuite

cfg = Config()
settings = RobotSettings()
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


class ClusteringTests(object):

    def __init__(self):
        logging.info('Init docker client')
        self.docker_client = \
            docker.Client(base_url='unix://var/run/docker.sock',
                          version='1.9', timeout=10)
        logging.info('Get list of containers')
        self.containers = self.docker_client.containers()

    def test_general_cluster_functionality(self):
        logging.info('Start general test')

        suites = cfg.suites
        suites = map(
            lambda x: unicode('/'.join([cfg.test_repo_path, cfg.suites_path, x])), suites)

        variablefile = '/'.join([cfg.test_repo_path,
                                 ':'.join([cfg.variablefile, cfg.topology_file])])

        variables = cfg.variables
        containers = [container for container in self.containers
                      if container['Names'][0][1:] in cfg.containers]
        if len(containers) != len(cfg.containers):
            logging.info('Please check container names in config.cfg and check reachability of the marked containers')
            return

        ips = \
            [self.docker_client.inspect_container(container)['NetworkSettings']['IPAddress']
             for container in self.containers]


        logging.info('Iterate by containers')

        for container, ip in zip(containers, ips):
            variables['CONTROLLER'] = ip
            name = container['Names'][0][1:]
            logging.info('Start tests against {0} with ip {1}'.format(name, ip))
            _variables = [':'.join(param) for param in variables.iteritems()]

            run(*suites, include=cfg.tags, loglevel='DEBUG',
                log='{0}--log.html'.format(name),
                report='{0}--report.html'.format(name),
                output='{0}--output.html'.format(name),
                variablefile=variablefile,
                variable=_variables)

            logging.info('Stop container {0} with ip {1}'.format(name, ip))
            self.docker_client.pause(container['Id'])

            logging.info('Waiting for finish of election. Sleep {0}sec'.format(cfg.upstart_timeout))
            sleep(cfg.votes_timeout)

            other_ips = filter(lambda x: x != ip, ips)
            other_containers = filter(lambda x: x != container, containers)

            for _container, _ip in zip(other_containers, other_ips):
                variables['CONTROLLER'] = _ip
                _name = _container['Names'][0][1:]
                logging.info('Start tests against {0} with ip {1}'.format(_name, _ip))
                _variables = [':'.join(param)
                              for param in variables.iteritems()]
                run(*suites, include=cfg.tags, loglevel='DEBUG',
                    log='{0}-{1}--log.html'.format(name, _name),
                    report='{0}-{1}--report.html'.format(name, _name),
                    output='{0}-{1}--output.html'.format(name, _name),
                    variablefile=variablefile,
                    variable=_variables)

            logging.info('Unpause {0} with ip {1}'.format(name, ip))
            self.docker_client.unpause(container['Id'])

            logging.info('Waiting for finish of election. Sleep {0}sec'.format(cfg.upstart_timeout))
            sleep(cfg.upstart_timeout)

if __name__ == '__main__':
    a = ClusteringTests()
    a.test_general_cluster_functionality()
