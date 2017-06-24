"""
    Usage:
        apiapi.py (all|mutating) [--csv=output_file]
"""

import csv
from policyuniverse import global_permissions
import re
from tabulate import tabulate


TAGS = {
    'DATA_PLANE': ['object', 'bucket'],
    'CONTROL_PLANE': ['policy', 'attribute', 'permission'],
    'MUTATING': ['create', 'delete', 'modify', 'add', 'remove', 'set', 'update', 'put'],
    'READ': ['get', 'view', 'list', 'describe'],
    'SIDE_EFFECT': ['start', 'stop', 'export', 'request', 'resend', 'cancel', 'continue', 'estimate', 'execute', 'preview']
}

permissions = dict()
for service_name, service_description in global_permissions.items():
    service = service_description['StringPrefix']
    permissions[service] = dict()
    for action in service_description['Actions']:

        action_words = re.findall('[A-Z][^A-Z]*', action)
        action_words = [word.lower() for word in action_words]
        permissions[service][action] = set()

        for tag_name, matches in TAGS.items():
            for match in matches:
                try:
                    if match in action_words:
                        permissions[service][action].add(tag_name)
                except IndexError:
                    if action.lower().startswith(match):
                        permissions[service][action].add(tag_name)

headers = ['service', 'permission']
headers.extend(TAGS.keys())


def create_permissions_table():
    rows = []
    for service, actions in permissions.items():
        for action, tags in actions.items():
            row = [service, action]

            for tag in TAGS.keys():
                row.append(tag in tags)

            rows.append(row)
    return rows


def create_mutating_table():
    """ Filters permissions by MUTATING or SIDE_EFFECT tag. """
    rows = []
    for service, actions in permissions.items():
        for action, tags in actions.items():
            row = [service, action]

            for tag in TAGS.keys():
                row.append(tag in tags)

            # CONTROL_PLANE && (MUTATING or SIDE_EFFECT)
            # if 'CONTROL_PLANE' in tags:
            if 'MUTATING' in tags:
                rows.append(row)
            if 'SIDE_EFFECT' in tags:
                rows.append(row)
    return rows


def output_csv(filename, rows):
    with open(filename, 'wb') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)
            for row in rows:
                csv_writer.writerow(row)


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, version="APIAPI 1.0")
    if args.get('mutating'):
        rows = create_mutating_table()
    elif args.get('all'):
        rows = create_permissions_table()

    filename = args.get('--csv')

    if filename:
        output_csv(filename, rows)
    else:
        print tabulate(rows, headers=headers)
