# Collective Mind
#
# See cM LICENSE.txt for licensing details.
# See cM COPYRIGHT.txt for copyright details.
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
    if os.path.isdir(fn) and fn.startswith(px3) and not fn.startswith('lib-'):
       # Load config
       p1=os.path.join(fn,px1,px2)

       success=True

       print 'Loading '+fn+' ...'

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

             sf=array['source_files']

             array['source_files_templates']=[]

             # Check if source files has CM_KERNEL
             found=False
             for q in sf:
                 p2=os.path.join(fn,q)
                 f=file(p2)
                 sx=f.read()
                 f.close()

                 sx=sx.replace('\r','')

                 if '"KERNEL_START"' in sx or '"ACC_KERNEL_START"' in sx:
                    print '  Found OpenME directives in '+q 

                    i=sx.find('#include')
                    if i<0:
                       print '#include not found!'
                    else:
                       sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_INCLUDE */\n\n'+sx[i:]
                       sx=sx1

                       t='openme_callback("PROGRAM_START", NULL);\n#endif'
                       i=sx.find(t)
                       if i<0:
                          print 'PROGRAM_START not found!'
                       else:
                          i+=len(t)+1
                          sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_PROGRAM_START */\n\n'+sx[i:]
                          sx=sx1

                          t='#ifdef OPENME\n  openme_callback("PROGRAM_END", NULL);'
                          i=sx.find(t)
                          if i<0:
                             print 'PROGRAM_END not found!'
                          else:
                             sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_PROGRAM_END */\n\n'+sx[i:]
                             sx=sx1

                             t='openme_callback("KERNEL_START", NULL);\n#endif'
                             i=sx.find(t)
                             if i<0:
                                print 'KERNEL_START not found!'
                             else:
                                i+=len(t)+1
                                sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_KERNEL_START */\n\n'+sx[i:]
                                sx=sx1

                                t='#ifdef OPENME\n  openme_callback("KERNEL_END", NULL);'
                                i=sx.find(t)
                                if i<0:
                                   print 'KERNEL_END not found!'
                                else:
                                   sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_KERNEL_END */\n\n'+sx[i:]
                                   sx=sx1

                                   t='openme_callback("ACC_KERNEL_START", NULL);\n#endif'
                                   i=sx.find(t)
                                   if i>=0:
                                      i+=len(t)+1
                                      sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_ACC_KERNEL_START */\n\n'+sx[i:]
                                      sx=sx1

                                   t='#ifdef OPENME\n  openme_callback("ACC_KERNEL_END", NULL);'
                                   i=sx.find(t)
                                   if i>=0:
                                      sx1=sx[:i].strip()+'\n\n/* CM_TEMPLATE_ACC_KERNEL_END */\n\n'+sx[i:]
                                      sx=sx1

                                   f=file(p2+'.cm_template','w')
                                   f.write(sx)
                                   f.close()

                                   array['source_files_templates'].append(q)
                                   found=True

             if found:
                try:
                   f=file(p1,'w')
                   f.write(json.dumps(array, indent=2, sort_keys=True)+'\n')
                   f.close()
                except Exception as e:
                   print 'Failed saving json file!'
                   exit(1)

                os.system('svn add '+os.path.join(fn, '*.cm_template'))
