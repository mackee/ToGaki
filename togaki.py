#! /usr/bin/env python
# ToGaki Command
# togaki <yaml>
# querying and verify in yaml

import yaml
import urllib
import json
import sys

def as_return(params, as_path):
    (paths, name) = as_path.split('->')
    paths = paths.split('#')
    for path in paths:
        try:
            if path.isdigit():
                params = params[int(path)]
            else:
                params = params[path]
        except:
            print 'FormatError: invalid "as" format'
    return (name, params)


def deep_ok(a, b, defpath=''):
    try:
        for b_key, b_value in b.iteritems():
            if a.has_key(b_key):
                if not isinstance(b_value, dict):
                    if a[b_key] != b_value:
                        raise KeyError, ('mismatch', defpath+b_key, a[b_key], b_value)
                else:
                    defpath += b_key+'#'
                    return deep_ok(a[b_key], b[b_key], defpath)
            else:
                raise KeyError, ('mismatch', defpath+b_key, None, None, b_value)
    except KeyError, inst:
        (types, key, got, definition) = inst
        print '================================'
        print 'type:', types
        print 'key:', key
        print 'got:', got
        print 'definition:', definition
        print '================================'
        return False
    return True


try:
    argv = sys.argv
    if len(argv) <= 1:
        exit('Usage: togaki.py <yaml-file>')
    f = open(argv[1]).read()
    reqres = yaml.load(f)
except (IOError, yaml.scanner.ScannerError):
    print 'Error: file not found'
    exit()

for i, test in enumerate(reqres['tests']):
    print i+1, ':', test['note']

    # request
    reqparam = [(k, v.encode('utf8')) for k, v in test['requests'].iteritems()]
    requests = urllib.urlencode(reqparam)
    url = test['url']+'?'+requests
    res = urllib.urlopen(url)
    
    # status check
    if test.has_key('status'):
        pass
    # response
    responses = json.loads(res.read())
    # as
    response_checks = {}
    for params in test['options']['as']:
        (name, value) = as_return(responses, params)
        response_checks[name] = value
    # checks
    for i, response in enumerate(test['responses']):
        if deep_ok(response_checks, response):
            print '  ' + 'subtest ' + str(i) + ' : ok'
        else:
            print '  ' + 'subtest ' + str(i) + ' : not ok'

