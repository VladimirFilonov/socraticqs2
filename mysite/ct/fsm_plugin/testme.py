from fsmspec import FSMSpecification

class START(object):
    '''example node plugin for automated test suite testing only.
    We adopt a convention of NODE names in ALL-CAPS and
    edge names in lower-case.
    This represents a START node.'''
    def get_path(self, node, state, request, **kwargs):
        'provide this method to generate URL for a node programmatically'
        return '/ct/some/where/else/'
    def start_event(self, node, fsmStack, request, **kwargs):
        'example event plugin method to intercept start event.'
        # do whatever analysis you want...
        # then if you want to trigger a transition, call it directly
        return fsmStack.state.transition(request, 'next', **kwargs)
        # otherwise just return None to indicate that generic UI
        # behavior should just continue as normal (i.e. your FSM is
        # not intercepting and redirecting this event.
    def next_edge(self, edge, state, request, **kwargs):
        'example edge plugin method to execute named transition'
        # do whatever processing you want...
        fsm = edge.fromNode.fsm
        mid = fsm.get_node('MID')
        return mid # finally return whatever destination node you want
    # node specification data goes here
    title = 'start here'
    path = 'ct:home'
    edges = (
            dict(name='next', toNode='END', title='go go go'),
        )


def get_specs():
    'get FSM specifications stored in this file'
    spec = FSMSpecification(name='test', title='try this',
            pluginNodes=[START], # nodes w/ plugin code
            nodeDict=dict( # all other nodes
                MID=dict(title='in the middle', path='ct:about'),
                END=dict(title='end here', path='ct:home'),
            ),
        )
    return (spec,)

