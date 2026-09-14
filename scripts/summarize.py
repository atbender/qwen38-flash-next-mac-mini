"""Summarize native Slotstream statistics without confusing tok/s and s/token."""
import argparse,json,statistics
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('files',nargs='+',type=Path);a=p.parse_args()
for path in a.files:
 data=json.loads(path.read_text());s=data['stats'];dt=s['interTokenSeconds']
 out={'run':path.parent.name,'prompt_tokens':len(data['prompt_ids']),'output_tokens':len(data['output_ids']),
      'ttft_seconds':s.get('firstTokenSeconds'),'first_text_seconds':s.get('firstTextSeconds'),
      'mean_intertoken_seconds':statistics.mean(dt) if dt else None,
      'median_intertoken_seconds':statistics.median(dt) if dt else None,
      'intertoken_throughput':len(dt)/sum(dt) if dt and sum(dt)>0 else None,
      'native_decode_seconds':s['decodeSeconds'],'native_decode_tokens':s['decodeTokens'],
      'load_seconds':data['load_seconds'],'peak_process_gb':s['peakMemoryGB'],
      'finish_reason':s['finishReason'],'runtime_error':s.get('runtimeError'),'text':data['text']}
 print(json.dumps(out,indent=2))
