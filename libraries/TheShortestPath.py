import collections


class TheShortestPath(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        pass

    def select_the_shortest_path(self, routes):
        link_length = []
        routes = filter(
            lambda x: (x.get('route') and x.get('state') == 'up'), routes)
        routes.sort(key=lambda x: len(x.get('route')))
        necessary_route_id = routes[0].get('id')
        return necessary_route_id
