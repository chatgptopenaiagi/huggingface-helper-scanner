"""Build a provisional repository snapshot from allowlisted API fields only."""
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re

from hhs import __version__
from .client import Client, Failure, metadata_url
from .url_parser import InputError, parse_url, safe_path

STATES = {'OBSERVED','INFERRED','VERIFIED','UNVERIFIED','NOT_FOUND','ERROR','UNKNOWN'}
CODES = {'INVALID','UNSUPPORTED','PRIVATE','GATED','AUTH_REQUIRED','NOT_FOUND',
         'RATE_LIMITED','NETWORK_ERROR','TIMEOUT','MALFORMED_RESPONSE','UNKNOWN',
         'RESPONSE_TOO_LARGE','REDIRECT_BLOCKED','LIMIT_REACHED'}
WEIGHTS = {'safetensors','gguf','bin','pt','pth','ckpt','onnx','h5','hdf5','msgpack','tflite','pb'}
CONFIGS = {'config.json','tokenizer_config.json','generation_config.json','adapter_config.json',
           'model_index.json','preprocessor_config.json'}
SECRET = re.compile(r'(?:hf_[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|sk-(?:proj-)?[A-Za-z0-9_-]{16,}|https?://[^\s/@]+:[^\s/@]+@|-----BEGIN [A-Z ]*PRIVATE KEY-----)', re.I)


def text(value, limit=200):
    if not isinstance(value, str) or len(value) > limit:
        raise Failure('MALFORMED_RESPONSE', 'Invalid or oversized allowlisted metadata field.')
    if SECRET.search(value) or re.search(r'(?i)(?:token|password|api[_-]?key|authorization|cookie)\s*[:=]', value):
        return '<redacted>'
    if re.search(r'(?i)(?:/home/[^/ ]+|[a-z]:\\+users\\+[^\\ ]+)', value):
        return '<redacted>'
    if any(ord(c)<32 or ord(c)==127 for c in value):
        raise Failure('MALFORMED_RESPONSE', 'Control characters in metadata field.')
    return value


def size(value):
    if value is not None and (type(value) is not int or not 0 <= value <= 2**63-1):
        raise Failure('MALFORMED_RESPONSE', 'Invalid reported file size.')
    return value


def oid(value, lengths=(40,64)):
    if value is None: return None
    if not isinstance(value,str) or len(value) not in lengths or not re.fullmatch('[0-9a-fA-F]+',value):
        raise Failure('MALFORMED_RESPONSE', 'Invalid object identity.')
    return value.lower()


def role(path):
    name=PurePosixPath(path).name.lower(); ext=PurePosixPath(name).suffix.lstrip('.')
    if name == 'adapter_config.json': return 'configuration'
    if 'adapter' in name and ext in WEIGHTS: return 'adapter'
    if ext in WEIGHTS: return 'model_weight'
    if name in CONFIGS: return 'configuration'
    if 'tokenizer' in name or name in {'vocab.json','merges.txt','special_tokens_map.json'}: return 'tokenizer'
    if name.startswith(('readme','license','licence')):
        return 'documentation' if name.startswith('readme') else 'license'
    if ext in {'md','rst'}: return 'documentation'
    if ext in {'py','js','ts','cpp','c','rs'}: return 'source_code'
    if ext in {'sh','bat','ps1'} or name == 'dockerfile': return 'script'
    if ext in {'parquet','csv','jsonl','arrow'}: return 'dataset'
    if 'quant' in name: return 'quantization'
    return 'unknown'


def repository_fields(data):
    result={}
    for key in ('private','gated'):
        val=data.get(key)
        if key=='private' and val is not None and type(val) is not bool:
            raise Failure('MALFORMED_RESPONSE','Invalid private flag.')
        if key=='gated' and val is not None and type(val) is not bool and val not in ('auto','manual'):
            raise Failure('MALFORMED_RESPONSE','Invalid gated flag.')
        result[key]=val
    for key in ('library_name','pipeline_tag'):
        result[key]=text(data[key]) if data.get(key) is not None else None
    tags=data.get('tags',[])
    if not isinstance(tags,list) or len(tags)>1000:
        raise Failure('MALFORMED_RESPONSE','Invalid or excessive tags.')
    result['tags']=[text(t) for t in tags]
    card=data.get('cardData')
    if card is not None and not isinstance(card,dict):
        raise Failure('MALFORMED_RESPONSE','Invalid card metadata.')
    license_value=(card or {}).get('license')
    if isinstance(license_value,list):
        if len(license_value)>100: raise Failure('MALFORMED_RESPONSE','Excessive license entries.')
        license_value=[text(v) for v in license_value]
    elif license_value is not None: license_value=text(license_value)
    result['license']=license_value
    return result


def file_fields(item):
    if not isinstance(item,dict) or not safe_path(item.get('rfilename')):
        raise Failure('MALFORMED_RESPONSE','Invalid file path in metadata.')
    path=text(item['rfilename'],1024)
    lfs=item.get('lfs')
    if lfs is not None:
        if not isinstance(lfs,dict): raise Failure('MALFORMED_RESPONSE','Invalid LFS metadata.')
        lfs={'sha256':oid(lfs.get('sha256'),(64,)), 'size_bytes':size(lfs.get('size')),
             'pointer_size_bytes':size(lfs.get('pointerSize'))}
    extension=PurePosixPath(path).suffix.lstrip('.').lower()
    return {'path':path,'type':'file','extension':extension,
            'size_bytes':size(item.get('size')), 'blob_id':oid(item.get('blobId')),
            'lfs':lfs,'lfs_status':'REPORTED' if lfs else 'NOT_REPORTED',
            'role':role(path),'role_state':'INFERRED','format':extension or None,
            'downloaded':False,'content_policy':'METADATA_ONLY','evidence_refs':[]}


def inspect_repository(url, revision=None, client=None):
    client=client or Client()
    now=datetime.now(timezone.utc).isoformat()
    snapshot={'snapshot_format':'hhs-repository-snapshot-0.1', 'hhs_inspector_version':__version__,
              'generated_at':now,'mode':client.mode,'status':'ERROR','source':None,
              'repository':{},'files':[], 'derived':{}, 'evidence':[], 'warnings':[], 'errors':[],
              'coverage':{'complete':False,'files_returned':0,'files_reported':None,
                          'max_files':client.limits.max_files,'max_pages':1,'pages_received':0},
              'accounting':{},'security':{'read_only':True,'credentials_used':False,
                    'repository_code_executed':False,'file_contents_retrieved':False,
                    'repository_content_untrusted':True}}
    api_url=None
    def evidence(state, subject, value, refs=()):
        identity=f'HF-{len(snapshot["evidence"])+1:04d}'
        source=snapshot['source'] or {}
        snapshot['evidence'].append({'id':identity,'subject':subject,'state':state,
            'confidence':0.5 if state=='INFERRED' else 0.0 if state in ('UNKNOWN','UNVERIFIED') else 0.95,
            'source':'synthetic_fixture' if client.mode=='offline_fixture' else 'huggingface_api' if api_url else 'url_parser',
            'method':'bounded metadata response' if api_url else 'deterministic URL parsing',
            'scope':'requested repository metadata only; no content or machine inspection',
            'observed_at':datetime.now(timezone.utc).isoformat(), 'url':api_url,
            'repo_id':source.get('repo_id'),'requested_revision':source.get('requested_revision'),
            'resolved_revision':source.get('resolved_revision'), 'references':list(refs),'value':value})
        return identity
    try:
        source=parse_url(url,revision)
        # Refuse credential-like identifiers without echoing the submitted URL.
        if any(SECRET.search(v) for v in source.values() if isinstance(v,str)):
            raise InputError('INVALID','Credential-like input is refused.')
        snapshot['source']=source
        evidence('UNVERIFIED','repository input',dict(source))
        if source['repo_type']!='model':
            raise Failure('UNSUPPORTED','Dataset and Space URL families are recognized; V0 inspects public model metadata only.')
        api_url=metadata_url(source)
        data,has_link=client.get_metadata(api_url)
        snapshot['coverage']['pages_received']=1
        if not isinstance(data,dict) or data.get('id')!=source['repo_id']:
            raise Failure('MALFORMED_RESPONSE','Repository response identity missing or mismatched.')
        source['resolved_revision']=oid(data.get('sha'),(40,))
        if source['resolved_revision'] is None:
            raise Failure('MALFORMED_RESPONSE','Resolved commit identity is missing.')
        requested=source['requested_revision']
        if requested and re.fullmatch('[0-9a-fA-F]{40}',requested) and requested.lower()!=source['resolved_revision']:
            raise Failure('MALFORMED_RESPONSE','Resolved commit does not match the explicitly requested commit.')
        repo=repository_fields(data)
        siblings=data.get('siblings')
        if not isinstance(siblings,list): raise Failure('MALFORMED_RESPONSE','File metadata list is missing or invalid.')
        files=[file_fields(item) for item in siblings[:client.limits.max_files]]
        if len({f['path'] for f in files})!=len(files):
            raise Failure('MALFORMED_RESPONSE','Duplicate or redaction-colliding file paths.')
        ref=evidence('OBSERVED','repository metadata',{'fields':repo,'response_sha256':client.response_hash})
        repo['evidence_refs']=[ref];snapshot['repository']=repo
        file_ref=evidence('OBSERVED','file metadata',{'reported_count':len(siblings),'retained_count':len(files),
                              'response_sha256':client.response_hash},[ref])
        inferred=evidence('INFERRED','filename and metadata classification',
                         {'rule':'V0 filename extensions/allowlist and library tag hints; no content validation'},[ref,file_ref])
        for f in files: f['evidence_refs']=[file_ref];f['role_evidence_refs']=[inferred]
        snapshot['files']=files
        snapshot['derived']={
            'weight_formats':sorted({f['format'] for f in files if f['role'] in ('model_weight','adapter')}),
            'possible_frameworks':[repo['library_name']] if repo['library_name'] else [],
            'possible_model_families':sorted(set(repo['tags']) & {'llama','bert','gpt2','mistral','qwen2','t5'}),
            'config_files':[f['path'] for f in files if f['role']=='configuration'],
            'documentation_files':[f['path'] for f in files if f['role']=='documentation'],
            'state':'INFERRED','evidence_refs':[inferred]}
        snapshot['coverage'].update(complete=len(files)==len(siblings) and not has_link,
                                    files_reported=len(siblings),files_returned=len(files))
        if not snapshot['coverage']['complete']:
            snapshot['warnings'].append({'code':'LIMIT_REACHED','reason':'File count or pagination limit reached; absence cannot be inferred.','evidence_refs':[file_ref]})
        for field in ('private','gated'):
            if repo[field]: snapshot['warnings'].append({'code':field.upper(),'reason':'API reports access restriction; no access attempted.','evidence_refs':[ref]})
        snapshot['status']='OK' if snapshot['coverage']['complete'] else 'PARTIAL'
    except (InputError,Failure) as exc:
        state='NOT_FOUND' if exc.code=='NOT_FOUND' else 'UNKNOWN' if exc.code in ('UNSUPPORTED','UNKNOWN') else 'ERROR'
        ref=evidence(state,'inspection outcome',{'code':exc.code,'reason':exc.reason})
        snapshot['errors'].append({'code':exc.code,'reason':exc.reason,'evidence_refs':[ref]})
    snapshot['accounting']={'requests_attempted':client.requests,'max_requests':1,'max_pages':1,
        'retries':0,'timeout_seconds':client.limits.timeout,'response_byte_limit':client.limits.max_response_bytes,
        'metadata_body_bytes_retrieved':client.bytes_read if client.mode=='live' else 0,
        'fixture_body_bytes_read':client.bytes_read if client.mode=='offline_fixture' else 0,
        'network_requests_attempted':client.requests if client.mode=='live' else 0,
        'model_payload_bytes_retrieved':0,'file_content_bytes_retrieved':0,
        'note':'Body bytes only; excludes headers/TLS. A refused oversized stream may read one extra sentinel byte. Counts bytes returned by body reads, including partial reads before failure; excludes unread or transport-buffered bytes.'}
    validate_snapshot(snapshot)
    return snapshot


def validate_snapshot(snapshot):
    """Dependency-free output contract and semantic checks, not a Manifest V1 validator."""
    def require(ok):
        if not ok: raise ValueError('Invalid repository snapshot structure or semantic references.')
    require(isinstance(snapshot,dict))
    keys={'snapshot_format','hhs_inspector_version','generated_at','mode','status','source','repository',
          'files','derived','evidence','warnings','errors','coverage','accounting','security'}
    require(set(snapshot)==keys)
    require(snapshot['snapshot_format']=='hhs-repository-snapshot-0.1')
    require(snapshot['hhs_inspector_version']=='0.1.0')
    require(snapshot['mode'] in ('live','offline_fixture'))
    require(snapshot['status'] in ('OK','PARTIAL','ERROR'))
    try: require(datetime.fromisoformat(snapshot['generated_at']).tzinfo is not None)
    except (TypeError,ValueError): raise ValueError('Invalid snapshot timestamp.') from None
    for key in ('repository','derived','coverage','accounting','security'):require(isinstance(snapshot[key],dict))
    for key in ('files','evidence','warnings','errors'):require(isinstance(snapshot[key],list))
    source=snapshot['source']
    require(source is None or isinstance(source,dict))
    if source is not None:
        require(set(source)=={'provider','host','repo_type','repo_id','owner','name',
                              'requested_revision','effective_revision','requested_path','resolved_revision'})
        require(source['provider']=='huggingface' and source['host']=='huggingface.co')
        require(source['repo_type'] in ('model','dataset','space'))
        require(all(isinstance(source[k],str) and bool(source[k]) for k in ('repo_id','owner','name','effective_revision')))
        require(source['repo_id']==source['owner']+'/'+source['name'])
        require(source['requested_revision'] is None or isinstance(source['requested_revision'],str))
        require(source['requested_path'] is None or safe_path(source['requested_path']))
        require(source['resolved_revision'] is None or isinstance(source['resolved_revision'],str)
                and bool(re.fullmatch('[0-9a-f]{40}',source['resolved_revision'])))
    require(snapshot['security']=={'read_only':True,'credentials_used':False,'repository_code_executed':False,
                                  'file_contents_retrieved':False,'repository_content_untrusted':True})
    require(all(type(v) is bool for v in snapshot['security'].values()))
    ids=[]
    for e in snapshot['evidence']:
        require(isinstance(e,dict) and isinstance(e.get('id'),str) and bool(e['id']))
        require(isinstance(e.get('references'),list) and all(r in ids for r in e['references']))
        ids.append(e['id']);require(e.get('state') in STATES)
        require(type(e.get('confidence')) in (int,float) and 0<=e['confidence']<=1)
        require(all(isinstance(e.get(k),str) and bool(e[k]) for k in ('source','method','scope','observed_at')))
        require('value' in e)
        try: require(datetime.fromisoformat(e['observed_at']).tzinfo is not None)
        except (TypeError,ValueError): raise ValueError('Invalid evidence timestamp.') from None
    require(len(ids)==len(set(ids)))
    def refs(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k.endswith('evidence_refs') or k=='references':
                    require(isinstance(v,list) and all(r in ids for r in v))
                refs(v)
        elif isinstance(x,list):
            for v in x: refs(v)
    refs(snapshot)
    for f in snapshot['files']:
        require(isinstance(f,dict) and isinstance(f.get('path'),str))
        require(set(f)=={'path','type','extension','size_bytes','blob_id','lfs','lfs_status','role','role_state',
                         'format','downloaded','content_policy','evidence_refs','role_evidence_refs'})
        require(f['type']=='file' and isinstance(f['extension'],str))
        require(f['lfs_status'] in ('REPORTED','NOT_REPORTED'))
        require(f['role'] in {'configuration','tokenizer','model_weight','adapter','dataset','documentation',
                             'source_code','script','license','quantization','unknown'})
        try:
            oid(f['blob_id'])
            if f['lfs'] is not None:
                require(isinstance(f['lfs'],dict) and set(f['lfs'])=={'sha256','size_bytes','pointer_size_bytes'})
                oid(f['lfs']['sha256'],(64,));size(f['lfs']['size_bytes']);size(f['lfs']['pointer_size_bytes'])
        except Failure: raise ValueError('Invalid snapshot object metadata.') from None
        require(f.get('downloaded') is False and f.get('content_policy')=='METADATA_ONLY')
        require(f.get('role_state')=='INFERRED')
        require(f.get('size_bytes') is None or type(f['size_bytes']) is int and f['size_bytes']>=0)
        require(bool(f.get('evidence_refs')) and bool(f.get('role_evidence_refs')))
    for failure in snapshot['warnings']+snapshot['errors']:
        require(isinstance(failure,dict) and failure.get('code') in CODES and isinstance(failure.get('reason'),str))
    accounting=snapshot['accounting']
    require(accounting.get('model_payload_bytes_retrieved')==0 and accounting.get('file_content_bytes_retrieved')==0)
    for key in ('requests_attempted','network_requests_attempted','metadata_body_bytes_retrieved','fixture_body_bytes_read',
                'model_payload_bytes_retrieved','file_content_bytes_retrieved'):
        require(type(accounting.get(key)) is int and accounting[key]>=0)
    require(accounting['requests_attempted']<=1 and accounting['network_requests_attempted']<=accounting['requests_attempted'])
    if snapshot['mode']=='offline_fixture':
        require(accounting['network_requests_attempted']==0 and accounting['metadata_body_bytes_retrieved']==0)
    require(snapshot['coverage'].get('files_returned')==len(snapshot['files']))
    require(type(snapshot['coverage'].get('complete')) is bool)
    require((snapshot['status']=='ERROR')==bool(snapshot['errors']))
    if snapshot['status']!='ERROR':
        require(isinstance(snapshot['source'],dict) and bool(snapshot['source'].get('resolved_revision')))
        require((snapshot['status']=='OK')==snapshot['coverage']['complete'])
