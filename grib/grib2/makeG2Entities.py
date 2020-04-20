import csv
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

conceptTemplate42 = ('@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
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
                   '\tskos:related <http://reference.metoffice.gov.uk/um/stash/m01s{ss}i{si}> ;\n'
                   '\t.\n')

conceptTemplate45 = ('@prefix skos:  <http://www.w3.org/2004/02/skos/core#> . \n'
                     '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n\n'
                     '<{cf}> a skos:Concept ;\n'
                     '\trdfs:label "{label}"@en ;\n'
                     '\tskos:notation "{cf}"@en ;\n'
                     '{u}'
                     '\t.\n')

def main():
    print('Make GRIB2 TTL contents')
    root_path = os.path.dirname(__file__)

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
            with open(fpath, 'w', encoding='utf-8') as fh:
                # unit is not fully populated yet
                ustr = ''
                if entity['Unit']:
                    ustr = '\t<http://codes.wmo.int/def/common/unit> "{}" ;\n'
                    ustr = ustr.format(entity['Unit'])
                fh.write(conceptTemplate42.format(d=entity['Discipline'],
                                                c=entity['Category'],
                                                n=entity['Number'],
                                                label=entity['Parameter'],
                                                u=ustr,
                                                ss=int(int(entity['STASH code'])/1000),
                                                si=int(entity['STASH code'])%1000))

    with open(os.path.join(root_path, 'mo--74/4.5.ttl'), 'w') as csf:
        csf.write(conceptScheme45)

    with open(os.path.join(root_path, 'GRIB2SurfaceLocalTable.csv'), encoding='utf-8') as cf:
        greader = csv.DictReader(cf)
        ttlpath = os.path.join(root_path, 'mo--74', '4.5')
        if not os.path.exists(ttlpath):
            os.mkdir(ttlpath)
        for entity in greader:
            fpath = os.path.join(ttlpath, '{}.ttl'.format(entity['Code figure']))
            with open(fpath, 'w', encoding='utf-8') as fh:
                ustr = ''
                if entity['Unit']:
                    ustr = '\t<http://codes.wmo.int/def/common/unit> "{}" ;\n'
                    ustr = ustr.format(entity['Unit'])
                fh.write(conceptTemplate45.format(cf=entity['Code figure'],
                                                label=entity['Parameter'],
                                                u=ustr))


if __name__ == '__main__':
    main()
