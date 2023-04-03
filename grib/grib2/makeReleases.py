import argparse
import csv
import glob
import os
import re
import shutil


riTemplate = ('@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n'
              '@prefix reg: <http://purl.org/linked-data/registry#> .\n'
              '@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .\n'
              '\n'
              '</{uri}> a skos:Concept ;\n'
              '\trdfs:label "{label}"@en ;\n'
              '.\n'
              '<> a reg:RegisterItem ;\n'
              '\treg:notation "{not}" ;\n'
              '\treg:definition [ reg:entity </{uri}> ] ;\n'
              '\t.')

release = ('@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
           '@prefix dct: <http://purl.org/dc/terms/> . \n'
           '@prefix ldp:   <http://www.w3.org/ns/ldp#> .\n'
           '@prefix reg:   <http://purl.org/linked-data/registry#> .\n'
           '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n'
           '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> . \n'
           '<{rel}> a reg:Register , skos:ConceptScheme , ldp:Container  ;\n'
           '\tldp:isMemberOfRelation skos:inScheme ;\n'
           '\tdct:dataAccepted "{rdate}"^^xsd:date ;\n'
           '\tdct:identifier {relno} ;\n'
           '\trdfs:label "Release of GRIB2 Met Office Local Table definitions."@en ;\n'
           '\tdct:description "Release of GRIB2 Met Office Local Table definitions Extending WMO GRIB2 code tables for cases where the defined centre number is 74."@en .')

lstr = re.compile('.*rdfs:label "([^"]*)".*', re.DOTALL)

def parse_arguments(content_root):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('release_id')
    parser.add_argument('--omit', default='',
                        help='list relative uris for omission from the release'
                        '(comma separated)')
    args = parser.parse_args()
    omissions = [os.path.join(content_root, '{}.ttl').format(o) for o in args.omit.split(',')]
    missing_omissions = []
    root_path = os.path.dirname(os.path.abspath(__file__))
    for o in omissions:
        if not os.path.exists(os.path.join(root_path, o)):
            missing_omissions.append(o)
    if missing_omissions:
        raise ValueError('listed omissions do not exist:\n{}'.format('\n'.join(missing_omissions)))
    return(omissions, args.release_id)

def build_release_content(content_root, release_id, relno, rdate, omissions,
                          releases):
    core_path = 'mo--74'
    root_path = os.path.join(content_root, core_path, release_id)
    release_paths = [os.path.join(content_root, core_path, r) for r in releases]
    if not os.path.exists(root_path):
        os.mkdir(root_path)
        for ttlf in glob.glob('**/*.ttl', recursive=True):
            ttlfp = os.path.abspath(ttlf)
            # skip encoded releases
            for rp in release_paths:
                if ttlfp.startswith(rp):
                    continue
            # skip omitted entities from release definition
            if ttlfp not in omissions:
                newf = os.path.join(root_path, ttlf.replace('mo--74/', ''))
                newf = root_path + ttlfp.replace(os.path.join(content_root, core_path), '')
                if not os.path.exists(os.path.dirname(newf)):
                    os.mkdir(os.path.dirname(newf))
                with open(newf, 'w') as fh:
                    with open(ttlfp) as inp:
                        inpc = inp.read()
                    if os.path.exists(ttlfp.replace('.ttl', '')):
                        fh.write(inpc)
                    else:
                        m = lstr.match(inpc)
                        label = ''
                        if m is not None:
                            label, = m.groups(1)
                        fh.write(riTemplate.format(**{'uri': ttlf.replace('.ttl', ''),
                                                      'not': os.path.basename(ttlf).replace('.ttl', ''),
                                                      'label': label}))
        # write the relese definition ttl file last, to avoid double writing
        # newf copies of individual register definitions
        with open(root_path + '.ttl', 'w') as rf:
            rf.write(release.format(**{'rel':release_id,'relno':relno, 'rdate':rdate}))


def parseReleaseDefs(content_root):
    with open(os.path.join(content_root, 'releases.csv')) as relf:
        reader = csv.DictReader(relf)
        releases = []
        for rel in reader:
            releases.append(rel.get('release'))
    with open(os.path.join(content_root, 'releases.csv')) as relf:
        reader = csv.DictReader(relf)
        for rel in reader:
            if os.path.exists(os.path.join(content_root, rel.get('release'))):
                #continue
                print('{} exists'.format(content_root))
            build_release_content(content_root, rel.get('release'),
                                  rel.get('notation'), rel.get('date'),
                                  rel.get('omissions(|)').split('|'), releases)

def main():
    content_root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(content_root):
        raise valueError('content root missing: {}'.format(content_root))
    parseReleaseDefs(content_root)
    #omissions, release_id = parse_arguments(content_root)
    #build_release_content(content_root, release_id, omissions)
    
if __name__ == '__main__':
    main()
