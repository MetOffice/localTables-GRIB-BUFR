import csv
import glob
import os

conceptScheme42 = ('@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
                   '@prefix dct: <http://purl.org/dc/terms/> . \n'
                   '@prefix ldp:   <http://www.w3.org/ns/ldp#> .\n'
                   '@prefix reg:   <http://purl.org/linked-data/registry#> .\n'
                   '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n\n'
                   '<4.2> a reg:Register , skos:ConceptScheme , ldp:Container  ;\n'
                   '\tldp:isMemberOfRelation skos:inScheme ;\n'
                   '\trdfs:label "Met Office Local Table Parameter Definitions"@en ;\n'
                   '\tdct:description "Met Office Local Table Parameter definitions '
                   'Extending WMO GRIB2 code table 4.2 for cases where the '
                   'defined centre number is 74."@en .\n')

conceptScheme45 = ('@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
                   '@prefix dct: <http://purl.org/dc/terms/> . \n'
                   '@prefix ldp:   <http://www.w3.org/ns/ldp#> .\n'
                   '@prefix reg:   <http://purl.org/linked-data/registry#> .\n'
                   '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n\n'
                   '<4.5> a reg:Register , skos:ConceptScheme , ldp:Container  ;\n'
                   '\tldp:isMemberOfRelation skos:inScheme ;\n'
                   '\trdfs:label "Met Office Local Table Surface Type Definitions"@en ;\n'
                   '\tdct:description "Met Office Local Table Surface Type definitions '
                   'Extending WMO GRIB2 code table 4.5 for cases where the '
                   'defined centre number is 74."@en .\n')

conceptTemplate42 = ('@prefix dct: <http://purl.org/dc/terms/> . \n'
                     '@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
                     '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n\n'
                     '<{d}-{c}-{n}> a skos:Concept ;\n'
                     '\trdfs:label "{label}"@en ;\n'
                     '\t<http://metarelate.net/vocabulary/index.html#identifier> '
                     '\t<http://codes.wmo.int/def/common/edition> , '
                     '\t<http://codes.wmo.int/def/common/centre> , '
                     '\t<http://codes.wmo.int/def/grib2/discipline> , '
                     '\t<http://codes.wmo.int/def/grib2/parameter> , '
                     '\t<http://codes.wmo.int/def/grib2/category> ;\n'
                     '\t<http://codes.wmo.int/def/common/centre> <http://codes.wmo.int/common/centre/74> ;\n'
                     '\t<http://codes.wmo.int/def/common/edition> <http://codes.wmo.int/codeform/grib2> ;\n'
                     '{u}'
                     '\t<http://codes.wmo.int/def/grib2/category> <http://codes.wmo.int/grib2/codeflag/4.1/{d}-{c}> ;\n'
                     '\t<http://codes.wmo.int/def/grib2/discipline> <http://codes.wmo.int/grib2/codeflag/0.0/{d}> ;\n'
                     '\t<http://codes.wmo.int/def/grib2/parameter> {n} ;\n'
                     '{stc}{desc}'
                     '\t.\n')

conceptTemplate45 = ('@prefix dct: <http://purl.org/dc/terms/> . \n'
                     '@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
                     '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n\n'
                     '<{cf}> a skos:Concept ;\n'
                     '\trdfs:label "{label}"@en ;\n'
                     '\tskos:notation "{cf}"@en ;\n'
                     '{u}'
                     '\t.\n')

def main():
    print('Make GRIB2 TTL contents')
    root_path = os.path.dirname(__file__)

    root_path = os.path.dirname(os.path.abspath(__file__))
    relFile = os.path.join(root_path, 'releases.csv')
    with open(relFile) as relf:
        reader = csv.DictReader(relf)
        releases = []
        for rel in reader:
            releases.append(os.path.join(root_path, 'mo--74', rel.get('release')))
    for ttlfile in glob.glob('**/*.ttl', recursive=True):
        ttlf = os.path.abspath(ttlfile)
        if not any([ttlf.startswith(r) for r in releases]):
            os.remove(ttlf)

    with open(os.path.join(root_path, 'mo--74/4.2.ttl'), 'w') as csf:
        csf.write(conceptScheme42)

    with open(os.path.join(root_path, 'GRIB2ParameterLocalTable.csv'), encoding='utf-8') as cf:
        greader = csv.DictReader(cf)
        ttlpath = os.path.join(root_path, 'mo--74', '4.2')
        if not os.path.exists(ttlpath):
            os.mkdir(ttlpath)
        for entity in greader:
            fpath = os.path.join(ttlpath,
                                 '{d}-{c}-{n}.ttl'.format(d=entity['Discipline'],
                                                          c=entity['Category'],
                                                          n=entity['Number']))
            # unit is not fully populated yet
            ustr = ''
            if entity['Unit']:
                ustr = '\t<http://codes.wmo.int/def/common/unit> "{}" ;\n'
                ustr = ustr.format(entity['Unit'])
            stcstr = ''
            if entity['STASH code']:
                tstr = ('\tskos:related <http://reference.metoffice.gov.uk/'
                        'um/stash/m01s{ss:02d}i{si:03d}> ;\n')
                stcstr = tstr.format(ss=int(int(entity['STASH code'])/1000),
                                     si=int(entity['STASH code'])%1000)
            descstr = ''
            if entity['Description']:
                descstr = '\tdct:description "{}"@en ;\n'.format(entity['Description'])
            dstr = conceptTemplate42.format(d=entity['Discipline'],
                                                c=entity['Category'],
                                                n=entity['Number'],
                                                label=entity['Parameter'],
                                                u=ustr, stc=stcstr, desc=descstr)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as fh:
                    fhdef = fh.read()
                    for a, b in zip(fhdef.split('\n'), dstr.split('\n')):
                        if a != b:
                            if 'skos:related' in a and 'skos:related' in b:
                                ostr = dstr.replace(b, '{}\n{}'.format(a, b))
                            else:
                                raise ValueError('{} respecified with alternate definition'.format(fpath))
            else:
                ostr = dstr
                
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write(ostr)

    with open(os.path.join(root_path, 'mo--74/4.5.ttl'), 'w') as csf:
        csf.write(conceptScheme45)

    with open(os.path.join(root_path, 'GRIB2SurfaceLocalTable.csv'), encoding='utf-8') as cf:
        greader = csv.DictReader(cf)
        ttlpath = os.path.join(root_path, 'mo--74', '4.5')
        if not os.path.exists(ttlpath):
            os.mkdir(ttlpath)
        for entity in greader:
            fpath = os.path.join(ttlpath, '{}.ttl'.format(entity['Code figure']))
            ustr = ''
            if entity['Unit']:
                ustr = '\t<http://codes.wmo.int/def/common/unit> "{}" ;\n'
                ustr = ustr.format(entity['Unit'])
            ostr = conceptTemplate45.format(cf=entity['Code figure'],
                                                label=entity['Parameter'],
                                                u=ustr)

            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as fh:
                    if fh.read != ostr:
                        raise ValueError('{} respecified with alternate definition'.format(fpath))
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write(ostr)


if __name__ == '__main__':
    main()
