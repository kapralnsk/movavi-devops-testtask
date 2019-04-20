import argparse
import os

SWITCH_STATE_DICT = {
    'blue': 'green',
    'green': 'blue'
}

def get_state():
    statefile_path = os.environ.get('DEPLOYMENT_STATEFILE')
    with open(statefile_path, 'r') as statefile:
        state = statefile.read()
    os.environ['CURRENT_DEPLOYMENT_STATE'] = state
    os.environ['NEW_DEPLOYMENT_STATE'] = SWITCH_STATE_DICT[state]
    
def switch_state():
    statefile_path = os.environ.get('DEPLOYMENT_STATEFILE')
    with open(statefile_path, 'w') as statefile:
        statefile.write(SWITCH_STATE_DICT[os.environ['DEPLOYMENT_STATE']])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--get', dest='get_state')
    parser.add_argument('--switch', dest='switch_state')
    args = parser.parse_args()
    if args.get_state and args.switch_state:
        raise Exception('only one operation at a time')
    if args.get_state:
        get_state()
    if args.switch_state:
        switch_state()