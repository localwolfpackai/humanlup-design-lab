import sys, json, glob
import numpy as np
from PIL import Image
def oklab(rgb):
    c=rgb/255.0
    c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    l=0.4122214708*c[...,0]+0.5363325363*c[...,1]+0.0514459929*c[...,2]
    m=0.2119034982*c[...,0]+0.6806995451*c[...,1]+0.1073969566*c[...,2]
    s=0.0883024619*c[...,0]+0.2817188376*c[...,1]+0.6299787005*c[...,2]
    l,m,s=np.cbrt(l),np.cbrt(m),np.cbrt(s)
    return np.stack([0.2104542553*l+0.7936177850*m-0.0040720468*s,1.9779984951*l-2.4285922050*m+0.4505937099*s,0.0259040371*l+0.7827717662*m-0.8086757660*s],-1)
names={"linear":"linear.app","vercel":"vercel.com","awwwards":"awwwards.com","elevenlabs":"elevenlabs.io","component":"component.gallery"}
out={}
for f in sorted(glob.glob(sys.argv[1]+"/*.jpg")):
    key=[k for k in names if k in f][0]
    a=np.asarray(Image.open(f).convert("RGB")).reshape(-1,3).astype(np.int64)
    N=len(a)
    b=(a>>3); idx=(b[:,0]<<10)|(b[:,1]<<5)|b[:,2]
    cnt=np.bincount(idx,minlength=32768)
    sums=np.stack([np.bincount(idx,weights=a[:,i],minlength=32768) for i in range(3)],1)
    nz=np.nonzero(cnt)[0]; order=nz[np.argsort(-cnt[nz])]
    centers=[];labs=[];counts=[]
    for i in order:
        col=sums[i]/cnt[i]; lab=oklab(col)
        if labs:
            d=np.sqrt(((np.array(labs)-lab)**2).sum(1)); j=d.argmin()
            if d[j]<0.04: counts[j]+=cnt[i]; continue
        centers.append(col);labs.append(lab);counts.append(cnt[i])
    labs=np.array(labs);counts=np.array(counts);centers=np.array(centers)
    C=np.sqrt(labs[:,1]**2+labs[:,2]**2)
    keep=(counts>=40)|((counts>=14)&(C>0.08))
    ia=set(np.argsort(-counts*keep)[:26]); il=set(np.argsort(-(C**2)*(counts**0.25)*keep)[:30])
    sel=[i for i in sorted(ia|il) if keep[i]]
    cl=[["#%02x%02x%02x"%tuple(int(round(v)) for v in centers[i]), round(counts[i]/N*100,4)] for i in sel]
    out[names[key]]=cl
    print(names[key],len(centers),"clusters; kept",len(cl),"sum %.1f"%sum(c[1] for c in cl))
    for h,s in sorted(cl,key=lambda x:-x[1])[:8]: print("   ",h,s)
json.dump(out,open("clusters.json","w"),separators=(",",":"))
