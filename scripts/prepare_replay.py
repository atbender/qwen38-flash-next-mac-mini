"""Reconstruct token arrival times from Slotstream's native callback intervals."""
import argparse,json
from pathlib import Path
from tokenizers import Tokenizer
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('stats',type=Path);p.add_argument('--tokenizer',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();data=json.loads(a.stats.read_text());s=data['stats'];ids=data['output_ids']
if s.get('runtimeError') or not ids:raise ValueError('No successful output')
tok=Tokenizer.from_file(str(a.tokenizer));dt=s['interTokenSeconds']
assert len(dt)==len(ids)-1,(len(dt),len(ids))
time=s['firstTokenSeconds'];events=[]
for i,tid in enumerate(ids):
 if i:time+=dt[i-1]
 events.append({'step':i,'token':tid,'seconds':time,'text':tok.decode(ids[:i+1],skip_special_tokens=True)})
assert events[-1]['text']==data['text'], 'Decoded text mismatch'
result={'model':'Qwen3.8-Flash-Next','runtime':'Slotstream 0.2.17','quantization':'MLX affine 4-bit checkpoint','events':events,'first_token_seconds':s['firstTokenSeconds'],'mean_intertoken_seconds':sum(dt)/len(dt) if dt else None,'total_seconds':s['prefillSeconds']+s['decodeSeconds'],'load_seconds':data['load_seconds'],'peak_process_gb':s['peakMemoryGB'],'expert_cache_hit_rate':s['expertHitRate'],'expert_read_bytes':s['prefillReadBytes']+s['decodeReadBytes'],'stats':s}
a.out.write_text(json.dumps(result,indent=2))
