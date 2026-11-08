"""Streaming public-use CPS ASEC ZIP preflight; no household result is simulated.

The 2026 technical documentation reports 88,026 household, 61,133 family,
134,729 person SAS/CSV records. The archive is NOT bundled: run on a genuine
Census download and explicitly map exact member names before accepting counts.
"""
from __future__ import annotations
import csv,hashlib,zipfile
from pathlib import Path

PUBLISHED_2026_COUNTS={'household':88026,'family':61133,'person':134729}

class CPSDataError(ValueError):pass

def inspect_archive(path, member_map=None, max_uncompressed=1_000_000_000):
    path=Path(path)
    if not path.is_file():raise CPSDataError('CPS_ARCHIVE_NOT_ACQUIRED')
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        if len(members)>30:raise CPSDataError('UNEXPECTED_MEMBER_COUNT')
        for x in members:
            if x.is_dir():continue
            p=Path(x.filename.replace('\\','/'))
            if p.is_absolute() or '..' in p.parts:
                raise CPSDataError('UNSAFE_ZIP_PATH')
            if x.file_size>max_uncompressed:raise CPSDataError('OVERSIZED_INDIVIDUAL_FILE')
        if sum(x.file_size for x in members)>max_uncompressed:
            raise CPSDataError('ZIP_EXPANSION_LIMIT')
        files={x.filename for x in members if not x.is_dir()}
        if not files:raise CPSDataError('NO_SOURCE_MEMBERS')
        with path.open('rb') as raw:
            digest=hashlib.file_digest(raw,'sha256').hexdigest()
        out={'archive_sha256':digest,
             'archive_bytes':path.stat().st_size,'members':[],
             'status':'SOURCE_ARCHIVE_INSPECTED_NOT_YET_POLICY_SCORED'}
        for name in sorted(files):
            info=z.getinfo(name)
            out['members'].append({'filename':name,'uncompressed_bytes':info.file_size,'crc32':f'{info.CRC:08x}'})
        if member_map:
            if set(member_map)!=set(PUBLISHED_2026_COUNTS):
                raise CPSDataError('REQUIRES_HOUSEHOLD_FAMILY_PERSON_MEMBER_MAP')
            if len(set(member_map.values()))!=3 or not set(member_map.values()).issubset(files):
                raise CPSDataError('SOURCE_MEMBER_MAP_INVALID')
            count_results={}
            for kind,filename in member_map.items():
                with z.open(filename) as binary:
                    import io
                    wrapper=io.TextIOWrapper(binary,encoding='utf-8-sig',newline='')
                    reader=csv.reader(wrapper)
                    try:headers=next(reader)
                    except StopIteration:raise CPSDataError('EMPTY_CSV_MEMBER')
                    if len(headers)<2 or len(set(headers))!=len(headers):raise CPSDataError('INVALID_OR_DUPLICATE_HEADERS')
                    count=0
                    for r in reader:
                        if len(r)!=len(headers):raise CPSDataError('MALFORMED_CSV_RECORD')
                        count+=1
                    expected=PUBLISHED_2026_COUNTS[kind]
                    if count!=expected:raise CPSDataError(f'{kind.upper()}_COUNT_MISMATCH {count} != {expected}')
                    count_results[kind]={'member':filename,'records':count,'columns':len(headers),'matched_documented_count':True}
            out['validated_2026_record_counts']=count_results
            out['status']='CPS_CSV_SOURCE_RECORD_COUNTS_VALIDATED_NO_INCIDENCE_ESTIMATE'
        return out
