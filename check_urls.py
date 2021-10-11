import copy
import glob
import json
import os
import unittest

import rdflib
import rdflib.compare
import requests

import grib.grib2.makeG2Entities as makeG2

"""
This test script evaluates all folder which contain a file of name
'regurl'
that contains a single URL for a registry.

Test will succeed if the registry exists, and all contents is the same as
in the repository commit.

All entities must exist, evaluate to the same content, and no entities may be
remote that are not in the source tree.

"""

uploads = {'PUT': [],
           'POST': []}

class TestContentsConsistency(unittest.TestCase):
    #def test
    def test_prod_register(self):
        with open('prodRegister', 'r') as ph:
            p = ph.read().split('\n')[0]
            pr = requests.get(p)
            self.assertEqual(pr.status_code, 200)

    def check_result(self, result, expected, uploads, identityURI):
        lbr = ('\n#######inTestResult#######\n')
        lbe = ('\n#######inExpected#######\n')
        try:
            assert(rdflib.compare.isomorphic(result, expected))
        except AssertionError:
            ufile = '{}.ttl'.format(identityURI.split(rooturl)[1])
            uploads['PUT'].append(ufile)
        self.assertTrue(rdflib.compare.isomorphic(result, expected),
                        lbr + lbe.join([g.serialize(format='n3').decode("utf-8") for g in
                                        rdflib.compare.graph_diff(result,
                                                                  expected)[1:]]))
                        

with open('prodRegister', 'r') as fh:
    rooturl = fh.read().split('\n')[0]
    print('Running test with respect to {}'.format(rooturl))

# Clean all .ttl files from the source tree

for f in glob.glob('**/*.ttl', recursive=True):
    os.remove(f)

# Ensure that all TTL content is built from the input tables.

makeG2.main()


# Build test cases based on the TTL files within the repository,
# one test case per file.
for f in glob.glob('**/*.ttl', recursive=True):    
    relf = f.replace('.ttl', '')
    identity = '{}/{}'.format(rooturl, relf)

    def make_a_test(infile):
        identityURI = copy.copy(identity)
        def entity_exists(self):
            headers={'Accept':'text/turtle'}
            regr = requests.get(identityURI, headers=headers)
            try:
                assert(regr.status_code == 200)
            except AssertionError:
                ufile = '{}.ttl'.format(identityURI.split(rooturl)[1])
                uploads['POST'].append(ufile)
            msg = ('{} expected to return 200 but returned {}'
                   ''.format(identityURI, regr.status_code))
            self.assertEqual(regr.status_code, 200, msg)
        return entity_exists
    tname = 'test_exists_{}'.format(relf.replace('/', '_'))
    setattr(TestContentsConsistency, tname, make_a_test(f))

    def make_another_test(infile):
        identityURI = copy.copy(identity)
        def entity_consistent(self):
            headers={'Accept':'text/turtle'}
            regr = requests.get(identityURI, headers=headers)
            ufile = '{}.ttl'.format(identityURI.split(rooturl)[1].lstrip('/'))
            assert(regr.status_code == 200)
            expected = requests.get(identityURI, headers=headers)
            expected_rdfgraph = rdflib.Graph()
            expected_rdfgraph.parse(data=expected.text, format='n3')
            # print(expected)
            result_rdfgraph = rdflib.Graph()
            # print(identityURI)
            result_rdfgraph.parse(ufile, publicID=identityURI, format='n3')
            self.check_result(result_rdfgraph, expected_rdfgraph, uploads,
                              identityURI)
        return entity_consistent

    # skip uncheckable content, e.g. container registers
    # print(f)
    if f in ['grib/grib2/mo--74/4.2.ttl', 'grib/grib2/mo--74/4.5.ttl']:
        continue

    tname = 'test_consistent_{}'.format(relf.replace('/', '_'))
    setattr(TestContentsConsistency, tname, make_another_test(f))


if __name__ == '__main__':
    try:
        unittest.main()
    except Exception as e:
        import pdb; pdb.set_trace()
        raise e
    finally:
        print("uploads:\n'{}'".format(json.dumps(uploads)))
