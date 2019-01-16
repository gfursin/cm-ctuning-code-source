# Collective Mind
#
# See cM LICENSE.txt for licensing details.
# See cM Copyright.txt for copyright details.
#
# Developer(s): Grigori Fursin, started on 2011.09

# Misc scripts

import json
import os
import shutil

px1='.cm'
px2='data.json'
px3=''
px4='.c'

r1='openme_init("");'
r2='openme_init(NULL,NULL,NULL,0);'

dirList=os.listdir('.')
for fn in dirList:
    # Check if startswith
    if fn.startswith(px3):
       if os.path.isdir(fn):
          for k in os.listdir(fn):
              if k.endswith(px4):
                 fx=os.path.join(fn,k)

                 f=open(fx, 'r')
                 x=f.read()
                 f.close()

                 y=x.replace(r1,r2)
                 if x!=y:
                    print 'Found and replaced string in '+fx+' ...'
                    f=open(fx, 'w')
                    f.write(y)
                    f.close()
