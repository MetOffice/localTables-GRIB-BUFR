import copy
import glob
import json
import unittest

import rdflib
import requests

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

    def check_result(self, result, expected):
        lbr = ('\n#######inTestResult#######\n')
        lbe = ('\n#######inExpected#######\n')

        self.assertTrue(rdflib.compare.isomorphic(result, expected),
                        lbr + lbe.join([g.serialize(format='n3').decode("utf-8") for g in
                                        rdflib.compare.graph_diff(result,
                                                                  expected)[1:]]))

with open('prodRegister', 'r') as fh:
    rooturl = fh.read().split('\n')[0]
    print('Running test with respect to {}'.format(rooturl))



for f in glob.glob('**/*.ttl', recursive=True):    
    relf = f.rstrip('.ttl')
    identity = '{}/{}'.format(rooturl, relf)

    def make_a_test(infile):
        identityURI = copy.copy(identity)
        def entity_exists(self):
            regr = requests.get(identityURI)
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


if __name__ == '__main__':
    # unittest.main()
    try:
        unittest.main()
    except Exception as e:
        import pdb; pdb.set_trace()
        raise e
    finally:
        print("uploads:\n'{}'".format(json.dumps(uploads)))
