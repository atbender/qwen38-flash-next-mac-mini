"""Render native Slotstream token timestamps into a shareable measured replay."""
import argparse,bisect,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1440,1040,15
BG='#0b1118';PANEL='#121d28';BORDER='#263444';WHITE='#edf4fa';MUTED='#91a4b8';ORANGE='#ff9a4d';GOLD='#f0c56a'
def font(n,b=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf' if b else '/System/Library/Fonts/Supplemental/Arial.ttf',n)
def render(t,data,speed):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);ev=data['events'];end=ev[-1]['seconds'];done=t>=end
 idx=bisect.bisect_right([e['seconds'] for e in ev],t)-1
 def text(x,y,s,n=20,c=WHITE,b=False):d.text((x,y),s,font=font(n,b),fill=c)
 def box(x,y,w,h):d.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=PANEL,outline=BORDER)
 d.rectangle((0,0,W,5),fill=ORANGE)
 text(40,28,'LOCAL INFERENCE / MEASURED TOKEN REPLAY',15,ORANGE,True)
 text(40,59,'Qwen3.8-Flash-Next',42,WHITE,True)
 text(40,114,'Mac mini M1 · 16 GB RAM · 1 TB SSD',27,MUTED)
 text(40,152,'Slotstream 0.2.17 · MLX 4-bit checkpoint · SSD expert streaming',20,MUTED)
 text(1210,39,f'{speed:g}× REPLAY',22,ORANGE,True)
 stats=[('INFERENCE ELAPSED',f'{min(t,end):.1f} s'),('TIME TO FIRST TOKEN',f'{data["first_token_seconds"]:.2f} s' if idx>=0 else 'Waiting…'),('TOKENS / SECOND',f'{idx/(ev[idx]["seconds"]-ev[0]["seconds"]):.2f}' if idx>0 else '—')]
 for i,(label,value) in enumerate(stats):
  x=40+i*460;box(x,205,440,112);text(x+20,222,label,14,MUTED,True);text(x+20,252,value,34,ORANGE if i==0 else WHITE,True)
 box(40,337,1360,74);text(60,350,'PROMPT',13,ORANGE,True);text(60,371,'explain what is navier stokes',25)
 box(40,432,1360,384);text(60,448,'MODEL OUTPUT',14,MUTED,True);text(1185,448,f'{idx+1} / {len(ev)} tokens',17,ORANGE)
 raw=ev[idx]['text'] if idx>=0 else ''
 raw=raw.replace('**','').replace('### ','').replace('## ','')
 if not raw:text(60,505,'Processing prompt…',26,MUTED)
 else:
  lines=[]
  for para in raw.split('\n'):
   line=''
   for word in para.split():
    new=(line+' '+word).strip()
    if d.textlength(new,font=font(28))>1310 and line:lines.append(line);line=word
    else:line=new
   lines.append(line)
  for j,line in enumerate(lines[-8:]):text(60,489+j*38,line,28)
 box(40,836,440,100);text(60,851,'PROCESS MEMORY · RUN PEAK',14,MUTED,True);text(60,879,f'{data["peak_process_gb"]:.2f} GB',30,ORANGE,True)
 box(500,836,440,100);text(520,851,'EXPERT CACHE · DECODE HIT RATE',14,MUTED,True);text(520,879,f'{data["expert_cache_hit_rate"]*100:.1f}%',30,ORANGE,True)
 box(960,836,440,100);text(980,851,'EXPERT READS · RUN TOTAL',14,MUTED,True);text(980,879,f'{data["expert_read_bytes"]/1e9:.2f} GB',30,GOLD,True)
 text(40,958,f'{len(ev)}-token excerpt · measured callbacks · MTP off · loading excluded ({data["load_seconds"]:.1f} s separately)',17,MUTED)
 text(40,993,'Bottom cards are whole-run statistics. Expert reads include OS cache hits; they are not physical SSD traffic.',16,MUTED)
 return im
p=argparse.ArgumentParser();p.add_argument('replay',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--speed',type=float,default=2);a=p.parse_args()
data=json.loads(a.replay.read_text());end=data['events'][-1]['seconds'];duration=end/a.speed+5
a.out.parent.mkdir(parents=True,exist_ok=True)
proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(a.out)],stdin=subprocess.PIPE)
for i in range(math.ceil(duration*FPS)):proc.stdin.write(render(min(i/FPS*a.speed,end),data,a.speed).tobytes())
proc.stdin.close()
if proc.wait():raise RuntimeError('Encoding failed')
render(end,data,a.speed).save(a.out.with_suffix('.png'))
