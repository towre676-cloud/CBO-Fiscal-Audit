"""Run the strictly mechanical, NON-national record-level joint wage/VAT engine.

Source records may be synthetic fixtures or independently authenticated external
records. This CLI NEVER weights/aggregates them as nationally representative.
Avoid personal identifiers. Use pseudonymous record_id strings only.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fiscal_data.v11_joint import joint_wage_vat,Unidentified
IDPAT=re.compile(r'^[a-zA-Z0-9._-]{1,128}$')

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for ch in iter(lambda:f.read(2**20),b''):h.update(ch)
    return h.hexdigest()

def process(input_jsonl,output_jsonl,max_records=100000):
    inp=Path(input_jsonl);out=Path(output_jsonl)
    if not inp.is_file() or inp.resolve()==out.resolve():raise ValueError('input missing or output equals input')
    if max_records<1:raise ValueError('max_records must be positive')
    out.parent.mkdir(parents=True,exist_ok=True)
    seen=set();n=0;temp_path=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=out.parent,
          prefix=out.name+'.tmp-',suffix='.jsonl',delete=False) as tmp:
            temp_path=Path(tmp.name)
            with inp.open('r',encoding='utf-8') as f:
                for line_no,line in enumerate(f,1):
                    if not line.strip():raise Unidentified(f'blank record line {line_no} not allowed')
                    try:record=json.loads(line)
                    except json.JSONDecodeError as e:raise Unidentified(f'invalid JSON at line {line_no}: {e.msg}')
                    if not isinstance(record,dict):raise Unidentified('each line must be an object')
                    ident=record.get('record_id')
                    if not isinstance(ident,str) or not IDPAT.fullmatch(ident) or ident in seen:
                        raise Unidentified('record_id missing/invalid/duplicate; pseudonymous IDs required')
                    seen.add(ident)
                    n+=1
                    if n>max_records:raise Unidentified(f'exceeded max_records {max_records}')
                    result=joint_wage_vat(record)
                    tmp.write(json.dumps({'record_id':ident,'result':result},default=str,separators=(',',':'),ensure_ascii=False)+'\n')
        os.replace(temp_path,out);temp_path=None
        return {'record_count':n,'original_input_sha256':digest(inp),
          'mechanical_output_sha256':digest(out),'full_12_provision_score':'NOT_CALCULATED',
          'population_or_national_score':'NOT_CALCULATED',
          'output_contains_pseudonymous_research_records':True,
          'survey_weighting_performed':False,'record_level_only':True}
    finally:
        if temp_path is not None:temp_path.unlink(missing_ok=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--max-records',type=int,default=100000)
    args=ap.parse_args()
    receipt=process(args.input,args.output,max_records=args.max_records)
    print(json.dumps(receipt,indent=2))
