"""Add native OOXML export properties after artifact-tool authoring; stdlib only.

The rendering engine documents HYPERLINK but does not calculate it in this
runtime. Keep authored display values and attach normal Excel relationships.
"""
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile
import xml.etree.ElementTree as E

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('',NS);E.register_namespace('r',R)

def patch(path,links_path):
    path=Path(path);links=json.loads(Path(links_path).read_text())
    with zipfile.ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
    wb=E.fromstring(files['xl/workbook.xml']);rels=E.fromstring(files['xl/_rels/workbook.xml.rels'])
    targets={r.attrib['Id']:r.attrib['Target'] for r in rels}
    sheets={s.attrib['name']:targets[s.attrib['{'+R+'}id']] for s in wb.find('{'+NS+'}sheets')}
    grouped={}
    for link in links:grouped.setdefault(link['sheet'],[]).append(link)
    late={'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties',
          'cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF',
          'picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
    for name,items in grouped.items():
        target=sheets[name];sheetpath=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        sheet=E.fromstring(files[sheetpath]);rp=PurePosixPath(sheetpath)
        relpath=str(rp.parent/'_rels'/(rp.name+'.rels'))
        relationships=E.fromstring(files[relpath]) if relpath in files else E.Element('{'+P+'}Relationships')
        ids={r.attrib['Id'] for r in relationships}
        hyperlinks=sheet.find('{'+NS+'}hyperlinks')
        if hyperlinks is None:
            hyperlinks=E.Element('{'+NS+'}hyperlinks')
            index=next((i for i,child in enumerate(sheet) if child.tag.split('}')[-1] in late),len(sheet))
            sheet.insert(index,hyperlinks)
        for link in items:
            if link.get('validation_allow_blank'):
                matches=[v for v in sheet.findall('{'+NS+'}dataValidations/{'+NS+'}dataValidation')
                         if v.get('sqref')==link['cell']]
                if len(matches)!=1 or matches[0].get('type')!='list':
                    raise ValueError('Expected one exported list validation: '+name+' '+link['cell'])
                # This runtime does not export the documented allowBlank flag.
                matches[0].set('allowBlank','1')
                continue
            if link['target'].startswith('#'):
                E.SubElement(hyperlinks,'{'+NS+'}hyperlink',{'ref':link['cell'],'location':link['target'][1:]})
                continue
            n=1
            while 'rId'+str(n) in ids:n+=1
            rid='rId'+str(n);ids.add(rid)
            E.SubElement(hyperlinks,'{'+NS+'}hyperlink',{'ref':link['cell'],'{'+R+'}id':rid})
            E.SubElement(relationships,'{'+P+'}Relationship',{'Id':rid,'Type':R+'/hyperlink',
                         'Target':link['target'],'TargetMode':'External'})
        files[sheetpath]=E.tostring(sheet,encoding='utf-8',xml_declaration=True)
        files[relpath]=E.tostring(relationships,encoding='utf-8',xml_declaration=True)
    tmp=path.with_suffix('.links.tmp')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in files.items():z.writestr(n,data)
    tmp.replace(path)
    print(json.dumps({'native_hyperlinks':sum('target' in x for x in links),
                      'blank_allowed_ranges':sum(bool(x.get('validation_allow_blank')) for x in links)}))

if __name__=='__main__':patch(*sys.argv[1:])
