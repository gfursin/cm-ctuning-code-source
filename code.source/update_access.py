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

dirList=os.listdir('.')
for fn in dirList:
    # Check if startswith
    if fn.startswith(px3):
       # Load config
       p1=os.path.join(fn,px1,px2)

       success=True

       try:
          f=file(p1)
       except Exception as e:
          success=False

       if success:
          try:
             array=json.loads(f.read())
          except Exception as e:
             print 'Error: ', e
             success=False

          if success:
             f.close()

             print 'Processing '+fn+' ...'

             array['cm_access_control']['read_groups']='all'

             # Writing updated array
             success=True
             try:
                f=file(p1,'w')
                f.write(json.dumps(array, indent=2, sort_keys=True)+'\n')
                f.close()
             except Exception as e:
                success=False

             if not success:
                print 'Failed!'
