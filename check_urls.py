import copy
import glob
import json
import os
import unittest

import rdflib
import rdflib.compare
import requests

import grib.grib2.makeG2Entities as makeG2
import grib.grib2.makeReleases as makeRels

"""
This test script evaluates all folder which contain a file of name
'regurl'
that contains a single URL for a registry.

Test will succeed if the registry exists, and all contents is the same as
in the repository commit.

All entities must exist, evaluate to the same content, and no entities may be
remote that are not in the source tree.

"""

def authenticate(session, base, userid, pss):
    auth = session.post('{}/system/security/apilogin'.format(base),
                        data={'userid':userid,
                                'password':pss})
    if not auth.status_code == 200:
        raise ValueError('auth failed')

    return session


# set up test environment
with open('prodRegister', 'r', encoding='utf-8') as fh:
    rooturl = fh.read().split('\n')[0].replace('http://', 'https://')

uploads = {'PUT': [],
           'POST': []}

outfile = os.environ.get('outfile', None)
if outfile is not None:
    if not os.path.exists(os.path.dirname(outfile)):
        raise ValueError('outfile directory does not exist: {}'.format(outfile))
    elif not os.access(os.path.dirname(outfile), os.W_OK):
        raise ValueError('outfile directory is not writeable: {}'.format(outfile))
    elif os.path.exists(outfile) and not os.access(outfile, os.W_OK):
        raise ValueError('outfile is not writeable: {}'.format(outfile))

# check for authenticated testing credentials
uname = os.environ.get('uname', None)
passcode = os.environ.get('passcode', None)

session = requests.Session()
if uname is not None and passcode is not None:
    session = authenticate(session, rooturl, uname, passcode)

# check for no failures running option
nofails = os.environ.get('nofails', None)
if nofails is None or not nofails:
    nofails = False
else:
    nofails = True

class TestContentsConsistency(unittest.TestCase):
    '''Test class, container for test generation below'''
    def test_prod_register(self):
        with open('prodRegister', 'r') as ph:
            p = ph.read().split('\n')[0]
            pr = requests.get(p)
            if nofails:
                self.assertTrue(True)
            else:
                self.assertEqual(pr.status_code, 200)

    def check_result(self, result, expected, uploads, identityURI):
        lbr = ('\n#######inTestResult#######\n')
        lbe = ('\n#######inExpected#######\n')
        try:
            assert(rdflib.compare.isomorphic(result, expected))
        except AssertionError:
            ufile = '{}.ttl'.format(identityURI.split(rooturl)[1])
            uploads['PUT'].append(ufile)
        if nofails:
            self.assertTrue(True)
        else:
            self.assertTrue(rdflib.compare.isomorphic(result, expected),
                            lbr + lbe.join([g.serialize(format='n3').decode("utf-8") for g in
                                            rdflib.compare.graph_diff(result,
                                                                      expected)[1:]]))

with open('prodRegister', 'r') as fh:
    rooturl = fh.read().split('\n')[0]
    print('Running test with respect to {}'.format(rooturl))

# Ensure that all TTL content is built from the input tables.

makeG2.main()
release_ids = makeRels.main()

# Build test cases based on the TTL files within the repository,
# one test case per file.
for f in glob.glob('**/*.ttl', recursive=True):
    release_file = False
    # release files with registerItem are tested differently
    if os.path.basename(f).startswith('_'):
        release_file = True
    relf = f.replace('.ttl', '')
    identity = '{}/{}'.format(rooturl, relf)

    # test generator, returning a test case suitable
    # for running as python unittest
    def make_a_test(infile):
        identityURI = copy.copy(identity)
        def entity_exists(self):
            headers={'Accept':'text/turtle'}
            regr = session.get(identityURI, headers=headers)
            try:
                assert(regr.status_code == 200)
            except AssertionError:
                ufile = '{}.ttl'.format(identityURI.split(rooturl)[1])
                uploads['POST'].append(ufile)
            msg = ('{} expected to return 200 but returned {}'
                   ''.format(identityURI, regr.status_code))
            if nofails:
                self.assertTrue(True)
            else:
                self.assertEqual(regr.status_code, 200, msg)
        return entity_exists
    tname = 'test_exists_{}'.format(relf.replace('/', '_'))
    # add test case for content file to test class
    setattr(TestContentsConsistency, tname, make_a_test(f))

    # test generator, returning a test case suitable
    # for running as python unittest
    def make_another_test(infile):
        identityURI = copy.copy(identity)
        def entity_consistent(self):
            headers={'Accept':'text/turtle'}
            regr = session.get(identityURI, headers=headers)
            ufile = '{}.ttl'.format(identityURI.split(rooturl)[1].lstrip('/'))
            if not nofails:
                msg = '{} returned {} not 200'.format(identityURI,
                                                      regr.status_code)
                assert(regr.status_code == 200), msg
            if regr.status_code == 200:
                result_rdfgraph = rdflib.Graph()

                result_rdfgraph.parse(ufile, publicID=identityURI, format='n3')
                expected = session.get(identityURI, headers=headers)
                expected_rdfgraph = rdflib.Graph()
                expected_rdfgraph.parse(data=expected.text, format='n3')
                if os.path.exists(identityURI.split(rooturl)[1].lstrip('/')):
                    # remove member entites from expected (tested elsewhere)

                    for fname in glob.glob('{}/*.ttl'.format(identityURI.split(rooturl)[1].lstrip('/'))):
                        member_id = rdflib.term.URIRef(u'{}/{}'.format(identityURI, fname.split('/')[-1].split('.ttl')[0]))
                        expected_rdfgraph.remove((None, rdflib.term.URIRef('http://purl.org/linked-data/registry#subregister'), None))
                        expected_rdfgraph.remove((member_id, None, None))

                        for r in release_ids:
                            if r in fname:
                                member_id = rdflib.term.URIRef(u'{}/{}'.format(identityURI.replace(r+'/', ''), fname.split('/')[-1].split('.ttl')[0].lstrip('_')))
                                expected_rdfgraph.remove((member_id, None, None))

                # do not check version info or date modified (owned by registry)
                expected_rdfgraph.remove((None, rdflib.namespace.DCTERMS.modified, None))
                expected_rdfgraph.remove((None, rdflib.namespace.OWL.versionInfo, None))
                self.check_result(result_rdfgraph, expected_rdfgraph, uploads,
                                  identityURI)
        return entity_consistent

    if not release_file:
        tname = 'test_consistent_{}'.format(relf.replace('/', '_'))
    # add test case for content file to test class
        setattr(TestContentsConsistency, tname, make_another_test(f))


if __name__ == '__main__':
    try:
        unittest.main()
    except Exception as e:
        raise e
    finally:
        print("uploads:\n'{}'".format(json.dumps(uploads)))
        if outfile is not None:
            with open(outfile, 'w') as ofh:
                ofh.write(json.dumps(uploads))
