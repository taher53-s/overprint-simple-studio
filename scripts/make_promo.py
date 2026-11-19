from pathlib import Path
import numpy as np, wave, subprocess, math, json
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'web'; TMP=ROOT/'build/promo'; TMP.mkdir(parents=True,exist_ok=True)
W,H,FPS,DUR=1280,720,24,42
PAPER='#f3f0e8';INK='#242720';ORANGE='#eb5f36'
@lru_cache(None)
def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
source=['#EE653A','#DF704D','#2D488B','#3D5692','#E9BF44','#EFCA5A','#2D332B','#3A4036']; inks=['#EC6033','#2D488B','#E9BF44','#2D332B']
def rgb(c):return tuple(bytes.fromhex(c[1:]))
def blend(a,b,t):return tuple(round(lerp(x,y,t)) for x,y in zip(rgb(a),rgb(b)))
before=Image.open(ROOT/'docs/original-study.png').convert('RGB');after=Image.open(ROOT/'docs/preview.png').convert('RGB')
# Original instrumental composition, 120 BPM, C-major/A-minor harmony.
SR=44100;N=SR*DUR;mix=np.zeros((N,2),dtype=np.float64);rng=np.random.default_rng(2409540)
def add(start,signal,pan=0):
 at=int(start*SR);length=min(len(signal),N-at)
 if length<=0:return
 mix[at:at+length,0]+=signal[:length]*math.sqrt((1-pan)/2);mix[at:at+length,1]+=signal[:length]*math.sqrt((1+pan)/2)
def hz(midi):return 440*2**((midi-69)/12)
chords=[[48,52,55,59],[45,48,52,55],[41,45,48,52],[43,47,50,55]]
for bar in range(21):
 chord=chords[bar%4];start=bar*2
 t=np.arange(int(2.5*SR))/SR;env=np.minimum(t/.18,1)*np.exp(-t/1.25)*np.minimum((2.5-t)/.3,1)
 for j,note in enumerate(chord):add(start,.028*env*(np.sin(2*np.pi*hz(note+12)*t)+.2*np.sin(2*np.pi*hz(note+24)*t)),(j-1.5)*.35)
 for beat in range(4):
  t=np.arange(int(.5*SR))/SR;add(start+beat*.5,.10*np.sin(2*np.pi*hz(chord[0]-12)*t)*np.exp(-t/ .18)*np.minimum(t/.008,1))
  t=np.arange(int(.22*SR))/SR;kick=np.sin(2*np.pi*(44*t+36*.025*(1-np.exp(-t/.025))))*.07*np.exp(-t/.06);add(start+beat*.5,kick)
  if beat in [1,3]:
   t=np.arange(int(.13*SR))/SR;noise=rng.normal(0,1,len(t));add(start+beat*.5,.016*(noise-np.roll(noise,1))*np.exp(-t/.025),.15)
 for tick in range(8):
  t=np.arange(int(.055*SR))/SR;noise=rng.normal(0,1,len(t));add(start+tick*.25,.005*(noise-np.roll(noise,1))*np.exp(-t/.009),-.3 if tick%2 else .3)
 for j,degree in enumerate([0,2,1,3]):
  t=np.arange(int(.65*SR))/SR;freq=hz(chord[degree]+24);pluck=.045*(np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*2*freq*t))*np.exp(-t/.17)*np.minimum(t/.01,1)
  add(start+j*.5+.25,pluck,(-.3,.3,-.15,.15)[j]);add(start+j*.5+.5,pluck*.2,.4)
fade=np.minimum(np.arange(N)/SR/1.8,1)*np.minimum((N-1-np.arange(N))/SR/2.5,1);mix*=fade[:,None]
peak=float(np.max(np.abs(mix)));mix*=.65/max(peak,1e-9)
with wave.open(str(TMP/'overprint-original-music.wav'),'wb') as audio:audio.setnchannels(2);audio.setsampwidth(2);audio.setframerate(SR);audio.writeframes((mix*32767).astype('<i2').tobytes())
print('Music composed:',DUR,'seconds; stereo; peak',round(float(np.max(np.abs(mix))),3),flush=True)
process=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(TMP/'overprint-original-music.wav'),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-af','loudnorm=I=-20:TP=-2:LRA=7','-t',str(DUR),'-movflags','+faststart',str(OUT/'overprint-film.mp4')],stdin=subprocess.PIPE,stderr=open(TMP/'motion-encode.log','w'))
headings=[('A poster. Eight colours.','Could similar colours share a printing ink?'),('Meet OVERPRINT.','A colour helper for printing posters.'),('Bring similar colours together.','In this example: 8 artwork colours → 4 suggested inks.'),('See before. See after.','Same poster. Different colour choices.'),('You choose how much changes.','Keep colours close, or allow a bigger change.'),('Check the colours that changed most.','If you do not like them, adjust and try again.'),('Fewer inks. Still your design.','Choose your colours. Compare the result. Save it.')]
def text(d,xy,value,size=24,bold=False,fill=INK):d.text(xy,value,font=font(size,bold),fill=fill)
def poster(im,pic,x,y,width):
 height=round(width*1.25);pic=pic.resize((round(width),height),Image.Resampling.LANCZOS);d=ImageDraw.Draw(im);d.rectangle((x+8,y+9,x+width+8,y+height+9),fill='#d4d3c8');im.paste(pic,(round(x),round(y)))
for frame in range(DUR*FPS):
 t=frame/FPS;s=min(6,int(t/6));local=t-s*6;u=local/6;e=ease(local/1.0);im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
 text(d,(50,26),'⊕  OVERPRINT',22,True);text(d,(1030,33),'COLOUR, CONSIDERED.',12,False,'#727768');d.line((50,70,1230,70),fill='#c9ccbf')
 title,subtitle=headings[s]
 if s not in [1,6]:text(d,(50,100+round(18*(1-e))),title,42,True);text(d,(52,164),subtitle,22,False,'#6a6f60')
 if s==0:
  for i,c in enumerate(source):
   startx=640+math.cos(i*math.pi/4)*660;starty=390+math.sin(i*math.pi/4)*330;x=lerp(startx,105+i*150,e);y=lerp(starty,390,e)+math.sin(t*2+i*.7)*18;r=48+3*math.sin(t*3+i);d.ellipse((x-r,y-r,x+r,y+r),fill=c)
  text(d,(50,535),'You made the design. Now explore the printing colours.',24)
 elif s==1:
  poster(im,before,round(lerp(1350,805,e)),100,410)
  text(d,(50,230),'Meet OVERPRINT.',55,True);text(d,(54,315),'A colour helper',32);text(d,(54,357),'for printing posters.',32)
  for j,label in enumerate(['Choose','Compare','Save']):
   x=54+j*220;y=470+round(25*(1-ease((local-j*.2)/1.1)));d.rounded_rectangle((x,y,x+192,y+58),radius=10,fill=ORANGE if j==1 else '#e1e3d7');text(d,(x+25,y+15),label,22,j==1)
 elif s==2:
  merge=ease((local-1.2)/2.5)
  for i,c in enumerate(source):
   family=i//2;x=lerp(80+i*147,120+family*295+(i%2)*4,merge);y=lerp(315,355+(i%2)*4,merge);width=lerp(115,225,merge);d.rounded_rectangle((x,y,x+width,y+155),radius=round(lerp(8,35,merge)),fill=blend(c,inks[family],merge))
  label='8 artwork colours' if merge<.5 else '4 suggested inks';text(d,(50,550),label,38,True)
 elif s==3:
  width=326;poster(im,before,90,220,width);poster(im,after,864,220,width)
  text(d,(90,625),'BEFORE · 8 COLOURS',14,True);text(d,(864,625),'AFTER · 4 INKS',14,True)
  x=477;y=240;thumb=before.resize((326,408));other=after.resize((326,408));wipe=round(326*(.5+.5*math.sin(local*1.15-1.6)));thumb.paste(other.crop((0,0,wipe,408)),(0,0));im.paste(thumb,(x,y));d=ImageDraw.Draw(im);d.line((x+wipe,y,x+wipe,y+408),fill=ORANGE,width=4)
 elif s==4:
  x=80;y=350;d.rounded_rectangle((x,y,1200,y+20),radius=10,fill='#d3d8c8');pos=.2+.6*(.5-.5*math.cos(local*1.05));knob=x+1120*pos;d.rounded_rectangle((x,y,knob,y+20),radius=10,fill=ORANGE);d.ellipse((knob-24,y-14,knob+24,y+34),fill=INK)
  text(d,(80,410),'Keep colours close',24);text(d,(905,410),'Allow more change',24)
  for j,c in enumerate(source[:4]):d.ellipse((100+j*94,510,160+j*94,570),fill=c)
  text(d,(560,520),'Try a setting. Look at the result. You decide.',22)
 elif s==5:
  result=json.loads((ROOT/'results/demo-plan.json').read_text())['result'];ids=result.get('rankedReview',result['review'])[:3]
  for j,i in enumerate(ids):
   enter=ease((local-j*.5)/1.2);x=65+j*410;y=round(lerp(750,280,enter));d.rounded_rectangle((x,y,x+370,y+250),radius=15,fill='#fffdf6',outline='#d6dacd',width=2);text(d,(x+24,y+22),f'Check {j+1}',27,True)
   m=result['mappings'][i];d.rounded_rectangle((x+24,y+80,x+164,y+168),radius=8,fill=m['source']);d.rounded_rectangle((x+205,y+80,x+345,y+168),radius=8,fill=m['ink']);text(d,(x+170,y+105),'→',25);text(d,(x+24,y+195),'Before',16);text(d,(x+205,y+195),'After',16)
  text(d,(65,575),'Your taste makes the final call.',26)
 elif s==6:
  poster(im,after,round(lerp(1310,820,e)),110,400)
  text(d,(50,200),'Fewer inks.',61,True);text(d,(50,281),'Still your design.',48)
  text(d,(54,375),'Choose. Compare. Save.',28,False,'#6a6f60')
  d.rounded_rectangle((54,460,480,528),radius=8,fill=ORANGE);text(d,(82,480),'Explore OVERPRINT  ↗',24,True)
  for j,c in enumerate(inks):r=19+3*math.sin(local*2+j);cx=80+j*62;d.ellipse((cx-r,583-r,cx+r,583+r),fill=c)
 d.line((50,676,1230,676),fill='#c9ccbf');d.rectangle((50,675,50+1180*(frame+1)/(DUR*FPS),678),fill=ORANGE)
 text(d,(50,692),'AN ON-SCREEN COLOUR STUDY · ALWAYS CHECK A REAL TEST PRINT',10,False,'#777b6e');text(d,(1120,691),f'{s+1:02d} / 07',11)
 if frame==round(8.5*FPS):im.save(OUT/'promo-poster.jpg',quality=93)
 if frame in [72,360,600,864]:im.save(TMP/f'motion-check-{frame}.jpg',quality=90)
 # Brief cream transitions create breathing room between scenes.
 edge=min(local,6-local);opacity=1 if s==0 and local<.2 else min(1,edge/.16)
 if opacity<1:im=Image.blend(Image.new('RGB',(W,H),PAPER),im,opacity)
 process.stdin.write(im.tobytes())
process.stdin.close();assert process.wait()==0
vtt=['WEBVTT\n']
for i,(a,b) in enumerate(headings):vtt.append(f'00:{i*6:02d}.000 --> 00:{(i+1)*6:02d}.000\n{a}\n{b}\n')
(OUT/'promo.vtt').write_text('\n'.join(vtt));print('Created motion video with music:',(OUT/'overprint-film.mp4').stat().st_size,'bytes',flush=True)
