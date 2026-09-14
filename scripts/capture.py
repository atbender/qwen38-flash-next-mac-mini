"""Capture a Slotstream run; preserve native metrics and timestamp stdout chunks."""
import argparse,codecs,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--binary',required=True)
p.add_argument('--model',required=True)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--prompt',default='explain what is navier stokes')
p.add_argument('--max-tokens',type=int,default=64)
p.add_argument('--memory-gb',type=float,default=8.5)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
cmd=[a.binary,'run','--model',a.model,'--prompt',a.prompt,'--max-tokens',str(a.max_tokens),
     '--max-context','512','--memory-gb',str(a.memory_gb),'--mtp','off','--vision','off',
     '--greedy','--stats-json',str(a.out/'stats.json')]
(a.out/'request.json').write_text(json.dumps({'prompt':a.prompt,'max_tokens':a.max_tokens,'memory_gb':a.memory_gb,'max_context':512,'mtp':False,'vision':False,'greedy':True},indent=2))
t=time.monotonic();decoder=codecs.getincrementaldecoder('utf-8')();text=''
with (a.out/'stderr.log').open('w') as err,(a.out/'stream.jsonl').open('w',buffering=1) as log:
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=err,bufsize=0)
 for chunk in iter(lambda:os.read(proc.stdout.fileno(),4096),b''):
  delta=decoder.decode(chunk)
  if delta:
   text+=delta
   log.write(json.dumps({'since_launch_seconds':time.monotonic()-t,'text':text,'delta':delta})+'\n')
 rc=proc.wait()
(a.out/'stdout.txt').write_text(text)
(a.out/'capture.json').write_text(json.dumps({'exit_code':rc,'launch_wall_seconds':time.monotonic()-t},indent=2))
raise SystemExit(rc)
