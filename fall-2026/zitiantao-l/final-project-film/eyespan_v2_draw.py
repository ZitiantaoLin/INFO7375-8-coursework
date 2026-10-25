"""EyeSpan V2: labelled conceptual correspondence and temporal interaction.

All camera geometry, gaze paths and predictions drawn here are constructed.
Supplied setup and dataset images remain unchanged source assets.
"""
from pathlib import Path
import math
from PIL import Image
import drawing_base as base
from drawing_base import Canvas, ease, lerp, robot, camera, page, box3d, tick
from drawing_base import INK, BG, GREY, KRAFT, PALE, ACCENT

ROOT=Path(__file__).resolve().parent
GREEN='#426A5A'
TITLES={
 'B00':'Different views. Shared attention.',
 'B01':'Look. Locate. Confirm. Grasp.',
 'B02':'I built RaycastGrasp',
 'B03':'A category is not an instance',
 'B04':'Three patterns. Three responses.',
 'B05':'Two views + gaze',
 'B06':'Open it. Watch it. Inspect it.',
 'B07':'From course concept to delivery',
 'B08':'Make the mapping checkable',
 'B09':'One controlled tabletop',
 'B10':'Stable can still be wrong',
 'B11':'A contract with explicit checks',
 'B12':'EyeSpan',
}


def selection(c, box, color=INK, width=7):
    x0,y0,x1,y1=box;k=25
    for pts in [[(x0,y0+k),(x0,y0),(x0+k,y0)],[(x1-k,y0),(x1,y0),(x1,y0+k)],
                [(x0,y1-k),(x0,y1),(x0+k,y1)],[(x1-k,y1),(x1,y1),(x1,y1-k)]]:
        c.line(pts,color,width)


def mug(c,x,y,s=1.,left=False):
    sign=-1 if left else 1
    hx=x+sign*62*s
    c.ellipse((hx-29*s,y-45*s,hx+29*s,y+27*s),fill=PALE,width=5)
    c.rect((x-50*s,y-89*s,x+50*s,y+48*s),fill='#E5DAC5',radius=15*s,width=5)
    c.ellipse((x-50*s,y-105*s,x+50*s,y-73*s),fill=PALE,width=5)
    return x-72*s,y-122*s,x+72*s,y+65*s


def view(c,box,yaw,active=None,gaze=None,lift=0.,ids=True):
    x0,y0,x1,y1=box;cx=(x0+x1)/2;cy=(y0+y1)/2+55
    c.rect(box,fill=PALE,outline='#D9D4C7',width=3,radius=22)
    angle=math.radians(yaw);scale=(x1-x0)/7.3
    def proj(x,y,z=0):
        return cx+(x*math.cos(angle)-y*math.sin(angle))*scale,cy+(x*math.sin(angle)+y*math.cos(angle))*.39*scale-z*scale
    corners=[proj(x,y) for x,y in [(-2.7,-1.5),(2.7,-1.5),(2.7,1.5),(-2.7,1.5)]]
    c.poly(corners,fill='#C7AE86',width=4)
    for x,y in (corners[0],corners[2]):c.line([(x,y),(x,y+62)],INK,7)
    objects=[('A',-1.05,-.15),('B',1.15,.3)]
    objects.sort(key=lambda z:z[1]*math.sin(angle)+z[2]*math.cos(angle))
    locations={}
    for label,x,y in objects:
        px,py=proj(x,y)
        depth=x*math.sin(angle)+y*math.cos(angle)
        size=.85+.035*depth
        label_y=py+125
        if label=='A':py-=lift
        bbox=mug(c,px,py,size,left=math.cos(angle)<0)
        locations[label]=(px,py,bbox)
        if ids:c.txt(label,px,label_y,34)
    if active:
        selection(c,locations[active][2])
    if gaze:
        px,py,_=locations[gaze];c.dot(px,py-35,12)
    return locations


def pair(c,selected='A',gaze='A',lift=0.,legend=True):
    l=view(c,(145,315,805,735),-28,gaze=gaze)
    r=view(c,(1115,315,1775,735),142,active=selected,lift=lift)
    c.txt('User view',475,275,40);c.txt('Robot view',1445,275,40)
    if legend:
        c.dot(635,810,11);c.txt('Gaze',675,810,34,anchor='lm')
        selection(c,(1060,795,1090,825),width=4);c.txt('Estimate',1120,810,34,anchor='lm')
    return l,r


def fit_image(c,path,box):
    # Compositing scale only; never create or hallucinate source-image detail.
    x0,y0,x1,y1=box;im=Image.open(path).convert('RGB')
    f=min((x1-x0)*c.s/im.width,(y1-y0)*c.s/im.height)
    im=im.resize((round(im.width*f),round(im.height*f)),Image.Resampling.LANCZOS)
    x=round((x0+x1)*c.s/2-im.width/2);y=round((y0+y1)*c.s/2-im.height/2)
    c.im.paste(im,(x,y))
    return x/c.s,y/c.s,(x+im.width)/c.s,(y+im.height)/c.s


def trace(c,points,progress,color=ACCENT,width=6):
    if progress<=0:return
    end=progress*(len(points)-1);n=int(end)
    out=points[:n+1]
    if n<len(points)-1:out=out+[lerp(points[n],points[n+1],end-n)]
    if len(out)>1:c.line(out,color,width)


def mechanism(c,x0,x1,name,kind,u):
    c.txt(name,(x0+x1)/2,310,43)
    a=440;b=590;left=x0+58;right=x1-20;w=right-left
    c.line([(left,700),(right,700)],GREY,3)
    c.txt('A',x0+15,a,34);c.txt('B',x0+15,b,34)
    c.line([(left,a),(right,a)],'#D9D4C7',18)
    c.line([(left,b),(right,b)],'#D9D4C7',18)
    if kind==0:
        pts=[(left,a),(right,a)]
        fill=min(1,u/.6);c.line([(left,a-55),(left+w*.6*fill,a-55)],INK,21)
        if u>.62:
            c.dot(left+w*.6,a,12,GREEN)
            c.txt('Request', (x0+x1)/2,775,36)
            c.txt('confirmation',(x0+x1)/2,821,36)
    elif kind==1:
        cut=left+w*.36
        pts=[(left,a),(cut,a),(cut,b),(right,b)]
        if u<.36:c.line([(left,a-55),(left+w*u,a-55)],INK,21)
        else:
            c.line([(cut-10,a-65),(cut+10,a-45)],INK,5);c.line([(cut+10,a-65),(cut-10,a-45)],INK,5)
            c.line([(cut,b-55),(cut+w*.64*min(1,(u-.36)/.6),b-55)],INK,21)
        if u>.36:c.txt('Reset',(x0+x1)/2,795,36)
    else:
        pts=[]
        for i in range(6):
            x=left+w*i/6;y=a if i%2==0 else b
            pts.extend([(x,y),(x+w/6,y)])
        c.txt('Keep waiting',(x0+x1)/2,795,36)
        for i in range(1,6):
            if i/6<u:
                xx=left+w*i/6;c.line([(xx-9,a-65),(xx+9,a-45)],INK,4);c.line([(xx+9,a-65),(xx-9,a-45)],INK,4)
    trace(c,pts,u)
    c.txt('time',(left+right)/2,730,32)


def render_frame(bid,t,duration,height=1080):
    u=max(0.,min(1.,t/duration));c=Canvas(height)
    c.txt('EYESPAN / PROJECT PITCH',135,78,32,anchor='lm')
    c.txt(TITLES[bid],135,155,62,anchor='lm',serif=True)
    c.txt(f'{int(bid[1:])+1:02d} / 13',1760,78,32,anchor='rm')
    footer='Constructed / proposed interaction'
    if bid=='B00':
        l,r=pair(c,selected='A' if u>.6 else None,gaze='A',legend=False)
        c.arrow((850,525),(1070,525),GREY)
        c.dot(*lerp((850,525),(1070,525),ease(u)),13)
        c.txt('Same object. Different viewpoints.',960,855,42)
    elif bid=='B01':
        lift=45*ease((u-.88)/.1)
        l,r=pair(c,selected='A' if u>.28 else None,gaze='A',lift=lift)
        c.arrow((850,525),(1070,525),GREY)
        if u>.58:tick(c,960,645,32)
        if u>.78:
            x,y,b=r['A'];p=ease((u-.78)/.12);spread=48-18*p
            gy=y-195+95*p-lift
            c.line([(x-spread,gy),(x-spread,gy+68),(x-16,gy+78)],INK,8)
            c.line([(x+spread,gy),(x+spread,gy+68),(x+16,gy+78)],INK,8)
        phase=0 if u<.28 else 1 if u<.58 else 2 if u<.78 else 3
        for j,(word,x) in enumerate(zip(['Look','Map','Confirm','Grasp'],[490,800,1120,1430])):
            c.txt(word,x,880,40)
            if j==phase:c.dot(x,925,8,INK)
    elif bid=='B02':
        b=fit_image(c,ROOT/'pantry/raycast_setup.png',(135,270,1335,850))
        labels=['Mixed reality','Eye tracking','Object detection','Robot control']
        for j,label in enumerate(labels):
            y=330+j*140;c.txt(label,1380,y,36,anchor='lm')
            if j<=min(3,int(u*4)):tick(c,1345,y,14)
        footer='Existing RaycastGrasp / prototype implemented by me'
        c.txt('Image supplied 24 Oct 2026',960,925,32)
    elif bid=='B03':
        l,r=pair(c,selected='A' if u>.58 else None,gaze='A')
        c.arrow((850,500),(1070,500),GREY)
        if u<.58:
            for k in ['A','B']:
                x,y,b=r[k];selection(c,b,GREY,4)
            c.txt('Category: cup',960,870,40)
        else:c.txt('Goal: the specific instance',960,870,40)
    elif bid=='B04':
        for j,name in enumerate(['Hold','Switch','Alternate']):
            x0=150+j*550;x1=x0+500
            mechanism(c,x0,x1,name,j,min(1,max(0,u*1.5)))
        c.dot(550,900,10);c.txt('Gaze target',580,900,32,anchor='lm')
        c.line([(985,900),(1040,900)],INK,18);c.txt('Dwell accumulation',1070,900,32,anchor='lm')
        footer='Constructed / threshold requests confirmation'
    elif bid=='B05':
        pair(c,selected='A',gaze='A',legend=False)
        c.arrow((845,525),(1075,525),GREY)
        c.txt('Images + gaze',960,820,42)
        c.txt('Device and execution calibration remain separate',960,890,34)
        c.dot(*lerp((850,525),(1060,525),ease(u)),12)
    elif bid=='B06':
        c.rect((180,290,1740,820),outline=GREY,radius=20)
        c.txt('First 60 seconds',960,245,42)
        page(c,480,535,1.25,play=True)
        c.arrow((665,535),(825,535),GREY)
        page(c,1020,430,.8);page(c,1020,680,.8)
        c.txt('Demo',480,755,40)
        c.txt('Code',1190,430,40,anchor='lm')
        c.txt('My contribution',1190,680,40,anchor='lm')
        c.dot(*lerp((665,535),(825,535),ease(u*2)),12)
        if u>.55:tick(c,1650,430,24)
        if u>.75:tick(c,1650,680,24)
        footer='Constructed / planned portfolio'
    elif bid=='B07':
        xs=[430,960,1490]
        c.line([(430,640),(1490,640)],GREY,5)
        page(c,xs[0],455,1.,check=True)
        box3d(c,xs[1],535,220,110,135)
        page(c,xs[2],455,1.,play=True)
        c.txt('Concept written',430,735,38)
        c.txt('Course build',960,735,38)
        c.txt('Demo + code',1490,735,38)
        c.dot(430+530*ease(min(1,u*1.5)),640,14)
        c.txt('Now',695,850,36);c.txt('Course end',1490,850,36)
        footer='Constructed / course-version delivery plan'
    elif bid=='B08':
        fit_image(c,ROOT/'pantry/dataset_overview_supplied.png',(135,285,1135,860))
        c.txt('Scene examples',635,245,40)
        c.txt('Planned check',1460,285,40)
        mug(c,1460,540,1.05)
        c.line([(1443,482),(1477,516)],GREEN,5);c.line([(1477,482),(1443,516)],GREEN,5)
        px=1570-40*ease(u);py=465
        c.dot(px,py,13,INK)
        c.line([(1475,495),(px-20,py+5)],GREY,4)
        c.line([(1268,678),(1292,702)],GREEN,5);c.line([(1292,678),(1268,702)],GREEN,5)
        c.dot(1280,745,12,INK)
        c.txt('Reference',1495,690,36)
        c.txt('Prediction',1495,745,36)
        c.txt('Time / target / settings',1455,840,32)
        c.txt('Figure supplied 24 Oct 2026',635,900,32)
        footer='Dataset scene examples / constructed comparison'
    elif bid=='B09':
        loc=view(c,(250,285,1415,805),-28,active='A',gaze='A')
        robot(c,1560,760,.85,reach=ease(u))
        c.txt('Stationary objects',820,870,40)
        c.txt('Target-user evaluation: future work',960,925,32)
        footer='Constructed / controlled tabletop scope'
    elif bid=='B10':
        mug(c,420,535,1.3);mug(c,745,535,1.3)
        c.txt('A',420,680,38);c.txt('B',745,680,38)
        sel='A' if u<.73 else 'B';x=420 if sel=='A' else 745
        selection(c,(x-96,365,x+96,630))
        gx=420+325*ease((u-.2)/.15);c.dot(gx,485,14)
        # Illustrative lag only; no measured delay or accuracy is shown.
        x0=1090;x1=1720;y0=425;y1=620
        c.txt('Gaze',1080,340,36,anchor='lm');c.txt('Estimate',1080,540,36,anchor='lm')
        trace(c,[(x0,y0),(1270,y0),(1270,y0+75),(x1,y0+75)],u,ACCENT,6)
        trace(c,[(x0,y1),(1510,y1),(1510,y1+75),(x1,y1+75)],u,INK,6)
        c.txt('Illustrative switching lag',1405,790,34)
        c.txt('Confirm or cancel before execution',960,890,38)
    elif bid=='B11':
        centers=[405,960,1515]
        c.rect((185,320,625,760),outline=GREY)
        c.rect((740,320,1180,760),outline=GREY)
        c.rect((1295,320,1735,760),outline=GREY)
        for x,title in zip(centers,['Inputs','Outputs','Checks']):c.txt(title,x,270,42)
        camera(c,405,440,.65)
        c.dot(405,570,13);c.txt('Views / gaze / time',405,680,32)
        mug(c,960,520,.8);selection(c,(880,385,1040,590))
        c.txt('Target + state',960,680,34)
        for i,label in enumerate(['Missing input','Invalid coordinates','Not confirmed']):
            y=405+i*115
            c.line([(1340,y-12),(1364,y+12)],INK,5);c.line([(1364,y-12),(1340,y+12)],INK,5)
            c.txt(label,1395,y,31,anchor='lm')
        c.arrow((650,540),(715,540),GREY);c.arrow((1205,540),(1270,540),GREY)
        if u>.5:c.txt('Reject before motion',960,870,40)
        footer='Constructed / proposed contract and test cases'
    elif bid=='B12':
        l,r=pair(c,selected='B' if u>.4 else 'A',gaze='B' if u>.25 else 'A',legend=False)
        c.arrow((850,525),(1070,525),GREY)
        c.txt('Two views. A changing target.',960,820,40)
        c.txt('Zitiantao Lin / Robotics perception + HRI',960,900,34)
    else:raise ValueError(bid)
    c.txt(footer,960,985,32)
    return c


if __name__=='__main__':
    base.render_frame=render_frame
    base.ROOT=ROOT
    base.main()
