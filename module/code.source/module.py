#
# Collective Mind
#
# See cM LICENSE.txt for licensing details.
# See cM COPYRIGHT.txt for copyright details.
#
# Developer(s): (C) Grigori Fursin, started on 2011.09
#

# Should always be here
ini={}
cm_kernel=None

# Local settings
import sys
import os
import shutil
import json
import time
import copy

# ============================================================================
def init(i):
    return {'cm_return':0}

# ============================================================================
def change_work_dir(i):

    """
    Chaning working directory

    Input:  {
              work_dir                  - if !='', go to this directory
              (work_dir_repo_uoa)       - if !='', go to the directory for this cM entry
              (work_dir_module_uoa)     - if !='', go to the directory for this cM entry
              (source_code_uoa)         - if !='', go to the directory for this cM entry
            }

    Output: {
              cm_return                 - if =0, success
              work_dir                  - selected working directory 
            }
    """

    # Changing working directory
    sys.stdout.flush()
    work_dir=''
    if 'work_dir' in i: work_dir=i['work_dir']
    elif ('work_dir_module_uoa' in i and 'source_code_uoa' in i):
       # Change path to another directory
       ii={'cm_run_module_uoa':i['work_dir_module_uoa'],
           'cm_action':'load',
           'cm_data_uoa':i['source_code_uoa']}
       if 'work_dir_repo_uoa' in i: ii['cm_repo_uoa']=i['work_dir_repo_uoa']
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r
       work_dir=r['cm_path']

    if work_dir!='':
       cm_kernel.print_for_con('Changing path to '+work_dir+' ...')
       os.chdir(work_dir)

    return {'cm_return':0, 'work_dir':work_dir}

# ============================================================================
def build(i):

    """
    Build program

    Input:  {
              See code.run (all parameters will be passed to code.run)

              (work_dir_repo_uoa)             - change to the working directory in the repository (repo UOA)
              (work_dir_module_uoa)           - change to the working directory in the repository (module UOA)
              (work_dir_data_uoa)             - change to the working directory in the repository (data UOA)

              build_target_os_uoa             - target OS uoa for building

              If the above parameters are set, the following parameters will be added to run_set_env2 from the given cM entry:
                CM_SOURCE_FILES="source_files"
                CM_SOURCE_FILES_WITHOUT_EXT="source_files" (extension will be removed)
                CM_TARGET_FILE="target_file"

              (target_file)                   - output file after building
              (add_target_extension)          - take extension from run_target_os_uoa
              (include_deps)                  - add 'include' directory from this list
              (include_prefix)                - add prefix before include directory (usually -I or /I) 
              (compiler_vars)                 - add compiler vars
              (compiler_var_prefix)           - add compiler var prefix (usually -D or /D)
              (lib_deps)                      - add libraries from this list (use CM_TARGET_FILE)

              (compilation_type)              - 'static' (by default) or 'dynamic'

              (install)                       - if 'yes', install to cM entry
              (install_data_uid)              - if !='', it will be used for installation data entry
              (install_data_alias)            - if !='', use it for installation data entry
              (install_data_display_as_alias) - use this display as alias for a generated entry
              (install_module_uoa)            - if =='', module 'code' is used
              (install_repo_uoa)              - repo for installation entry

              (source_files)                  - list of source files; if empty, use list of source files from the program entry

              (add_rem_to_script)             - add rem to install script
              (add_to_code_entry)             - add array to code entry

              (ignore_script_error)           - if 'yes', do not generate error when script returns !=0
                                                (needed for experiment pipelines to continue running)

              (cm_dependencies)               - dependencies that set all other dependencies (code/include/lib).
                                                Format [{"class UOA":"code UOA"},{},...]

              (skip_target_file_check)        - if 'yes', skip target file check

              (run_cmd_out1)                  - pass to 'code run' to redirect output1
              (run_cmd_out2)                  - pass to 'code run' to redirect output2

              (clean_program)                 - if 'yes', clean program before
              (clean_program_script_name)     - script name for cleaning ...

              (code_deps)                     - list with code UOA for dependencies [{"index":"uoa"} ...]

              (run_set_env2)                  - array with environment variables to be set before compiling
              (cm_verbose)                    - if 'yes', print all info
            }

    Output: {
              cm_return = 0, if successful

              Parameters from "code run" when executing script

              target_file      - output file after building
              target_file_size - size of output file
            }
    """

    # Check verbose - yes, by default
    vrb=i.get('cm_verbose','yes')

    if vrb=='yes':
       cm_kernel.print_for_con('***********************************************')
       cm_kernel.print_for_con('Building code ...')

    # Load target OS
    if vrb=='yes':
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con('Loading target os '+i['build_target_os_uoa']+' ...')
    ii={'cm_run_module_uoa':ini['cfg']['cm_modules']['os'],
        'cm_action':'load',
        'cm_data_uoa':i['build_target_os_uoa']}
    r=cm_kernel.access(ii)
    if r['cm_return']>0: return r

    target_os_cfg=r['cm_data_obj']['cfg']
    target_os_path=r['cm_path']
    target_os_uid=r['cm_uid']
    target_os_alias=r['cm_alias']

    # Dependencies
    code_deps=i.get('code_deps',[])
    include_deps=i.get('include_deps',[])
    lib_deps=i.get('lib_deps',[])
    compiler_vars=i.get('compiler_vars',[])

    # Check if code_deps set additional parameters
    qq=i.get('cm_dependencies',{})
    if len(qq)>0:
        if vrb=='yes':
           cm_kernel.print_for_con('')
           cm_kernel.print_for_con('Updating code/include/lib dependencies ...')

        code_deps1=[]
        include_deps1=[]
        lib_deps1=[]

        for q in i.get('cm_dependencies',{}):
            yy=q.keys()[0]
            x=q[yy]

            jj={'cm_run_module_uoa':ini['cfg']['cm_modules']['class'],
                'cm_data_uoa':yy,
                'cm_action':'load'}
            rj=cm_kernel.access(jj)
            if rj['cm_return']>0: return rj

            drj=rj['cm_data_obj']['cfg']

            vcd=drj.get('build_code_deps_var','')
            vid=drj.get('include_deps_var','')
            vld=drj.get('lib_deps_var','')

            if vcd!='': code_deps1.append({vcd:x})
            if vid!='': include_deps1.append({vid:x})
            if vld!='': lib_deps1.append({vld:x})

        for q in code_deps: code_deps1.append(q)
        for q in include_deps: include_deps1.append(q)
        for q in lib_deps: lib_deps1.append(q)

        code_deps=code_deps1
        include_deps=include_deps1
        lib_deps=lib_deps1

    i['code_deps']=code_deps

    if vrb=='yes':
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con('Code dependencies:')
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con(json.dumps(code_deps,indent=2))
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con('Include dependencies:')
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con(json.dumps(include_deps,indent=2))
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con('Lib dependencies:')
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con(json.dumps(lib_deps,indent=2))

    # Check if need to add some variables from code deps:

    if len(code_deps)>0:
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Updating variables from code dependencies ...')

       for q in code_deps:
           yy=q.keys()[0]
           x=q[yy]

           jj={'cm_run_module_uoa':ini['cfg']['cm_modules']['code'],
               'cm_data_uoa':x,
               'cm_action':'load'}
           rj=cm_kernel.access(jj)
           if rj['cm_return']>0: return rj

           drj=rj['cm_data_obj']['cfg']

           jj=drj.get('build_params',{})
           if len(jj)>0:
              cm_kernel.merge_arrays({'cm_array':i, 'cm_array1': jj})

    # Check a few special params
    include_prefix=i.get('include_prefix','')
    compiler_var_prefix=i.get('compiler_var_prefix','')

    # Check if install and prepare entry
    install=False
    if i.get('install', '')=='yes':
        install=True

        # Check if data_uoa is set and generate if not
        install_data_uid=''
        if 'install_data_uid' in i and i['install_data_uid']!='': install_data_uid=i['install_data_uid']
        install_data_alias=''
        if 'install_data_alias' in i: install_data_alias=i['install_data_alias']

        # Create install entry
        if vrb=='yes':
           cm_kernel.print_for_con('')
           cm_kernel.print_for_con('Creating installation entry ...')
        ii={'cm_action':'install',
            'cm_array':{'build_started':'yes',
                        'build_finished_successfully':'no'}}
        if 'add_to_code_entry' in i:
           ii['cm_array'].update(i['add_to_code_entry'])
        if len(code_deps)>0: ii['code_deps']=code_deps
        install_module_uoa=''
        if 'install_module_uoa' in i and i['install_module_uoa']!='':
           install_module_uoa=i['install_module_uoa']
           ii['install_module_uoa']=install_module_uoa
        else:
           install_module_uoa=ini['cfg']['cm_modules']['code']
        ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['code']
        if install_data_uid!='': ii.update({'install_data_uid':install_data_uid})
        if install_data_alias!='': ii.update({'install_data_uoa':install_data_alias})
        if 'install_data_display_as_alias' in i: ii['install_data_display_as_alias']=i['install_data_display_as_alias']
        install_repo_uoa=''
        if 'install_repo_uoa' in i and i['install_repo_uoa']!='': 
           install_repo_uoa=i['install_repo_uoa']
           ii['install_repo_uoa']=install_repo_uoa
# It seems that here should be host os and not target!
#        if 'build_target_os_uoa' in i and i['build_target_os_uoa']!='':
#           ii['target_os_uoa']=i['build_target_os_uoa']
        if 'run_host_os_uoa' in i and i['run_host_os_uoa']!='':
           ii['target_os_uoa']=i['run_host_os_uoa']
        if 'add_rem_to_script' in i:
           ii['add_rem_to_script']=i['add_rem_to_script']

        if vrb=='yes':
           ii['cm_verbose']=vrb

        r=cm_kernel.access(ii)
        if r['cm_return']>0: return r

        install_path=r['cm_path']
        install_uid=r['cm_uid']
        install_alias=r['cm_alias']
        script_name=r['script_name']
        script_filename=r['script_filename']

        if vrb=='yes':
           cm_kernel.print_for_con('')
           cm_kernel.print_for_con('Prepared entry:')
           cm_kernel.print_for_con(' path:   '+install_path)
           cm_kernel.print_for_con(' alias:  '+install_alias)
           cm_kernel.print_for_con(' UID:    '+install_uid)
           cm_kernel.print_for_con(' Script: '+script_name)

    # Check vars
    run_set_env2={}
    if 'run_set_env2' in i: run_set_env2.update(i['run_set_env2'])

    target_file=''
    if 'target_file' in i: target_file=i['target_file']

    obj_dir=''
    local_src_dir=''

    # Check that build in a cM entry, then set additional parameters
    sys.stdout.flush()

    force_includes=[]

    work_dir=''
    work_cfg={}
    if 'work_dir' in i: work_dir=i['work_dir']
    elif ('work_dir_module_uoa' in i and 'work_dir_data_uoa' in i):
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Loading parameters from the cM entry ...')

       # Change path to another directory
       ii={'cm_run_module_uoa':i['work_dir_module_uoa'],
           'cm_action':'load',
           'cm_data_uoa':i['work_dir_data_uoa']}
       if 'work_dir_repo_uoa' in i and i['work_dir_repo_uoa']!='': ii['cm_repo_uoa']=i['work_dir_repo_uoa']
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       work_cfg=r['cm_data_obj']['cfg']
       work_dir=r['cm_path']
       local_src_dir=''

       source_files=i.get('source_files',[])
       if len(source_files)==0:
          source_files=work_cfg.get('source_files',[])
       if len(source_files)>0: 
          jj=''
          jj1=''
          for j in source_files:
              jj+=' '+j
              jj1+=' '+os.path.splitext(j)[0]
          run_set_env2['CM_SOURCE_FILES']=jj
          run_set_env2['CM_SOURCE_FILES_WITHOUT_EXT']=jj1

       if target_file=='' and 'CM_TARGET_FILE' not in run_set_env2 and 'target_file' in work_cfg: 
          target_file=work_cfg['target_file']

       if 'local_src_dir' in work_cfg and work_cfg['local_src_dir']!='': 
          local_src_dir=work_cfg['local_src_dir']
       else:
          local_src_dir=work_dir

       # Check if need to add extension
       add_target_extension=i.get('add_target_extension','')
       if add_target_extension=='':
          add_target_extension1=work_cfg.get('add_target_extension',{})
          ct=i.get('compilation_type','')
          if ct=='': ct='static'
          if ct in add_target_extension1: add_target_extension=add_target_extension1.get(ct)

       if add_target_extension!='':
          if 'file_extensions' in target_os_cfg and add_target_extension in target_os_cfg['file_extensions']:
             target_ext=target_os_cfg['file_extensions'][add_target_extension]
             if vrb=='yes':
                cm_kernel.print_for_con('')
                cm_kernel.print_for_con('Adding target extension '+target_ext)

             target_file+=target_ext

          if 'obj_dir' in target_os_cfg:
             obj_dir=target_os_cfg['obj_dir']

       if 'force_build_includes' in work_cfg:
          force_includes=work_cfg['force_build_includes']

    if work_dir!='':
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Changing path to '+work_dir+' ...')
       os.chdir(work_dir)

    # Target file
    if target_file!='': 
       run_set_env2['CM_TARGET_FILE']=target_file

    if install:
       run_set_env2['CM_INSTALL']='yes'
       if install_path!='':
          run_set_env2['CM_INSTALL_DIR']=install_path
       if local_src_dir!='':
          run_set_env2['CM_INSTALL_LOCAL_DIR']=local_src_dir
       run_set_env2['CM_SRC_DIR']=work_dir
       if 'install_obj_dir' in ini['cfg'] and ini['cfg']['install_obj_dir']!='':
          obj_dir=ini['cfg']['install_obj_dir']
       if obj_dir!='':
          run_set_env2['CM_INSTALL_OBJ_DIR']=os.path.join(install_path, ini['cfg']['install_obj_dir'])
       if local_src_dir!='':
          run_set_env2['CM_LOCAL_SRC_DIR']=os.path.join(work_dir, local_src_dir)
       run_set_env2['CM_CODE_ENV_FILE']=script_name
       run_set_env2['CM_CODE_UID']=install_uid
       run_set_env2['CM_OS_LIB_DIR']=target_os_cfg['lib_dir']

    # Check if include dependencies
    if len(include_deps)>0 and include_prefix!='':
       ii={'cm_run_module_uoa':ini['cfg']['cm_modules']['code'],
           'cm_action':'prepare_env_for_all_codes',
           'code_deps':include_deps,
           'os_uoa':target_os_uid}
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       cm_compiler_flags_misc=''
       if 'CM_COMPILER_FLAGS_MISC' in run_set_env2: cm_compiler_flags_misc=run_set_env2['CM_COMPILER_FLAGS_MISC']

       for x in r['include_paths']:
           cm_compiler_flags_misc+=' '+include_prefix+x

       run_set_env2['CM_COMPILER_FLAGS_MISC']=cm_compiler_flags_misc

    # Add forced includes
    if len(force_includes)>0 and include_prefix!='':
       x=run_set_env2.get('CM_COMPILER_FLAGS_MISC','')
       for y in force_includes:
           x+=' '+include_prefix+y
       run_set_env2['CM_COMPILER_FLAGS_MISC']=x

    # Check if compiler_vars
    if len(compiler_vars)>0 and compiler_var_prefix!='':
       x=run_set_env2.get('CM_COMPILER_FLAGS_MISC','')

       for y in compiler_vars:
           z=y
           if compiler_vars[y]!='': z+='='+compiler_vars[y]
           x+=' '+compiler_var_prefix+z

       run_set_env2['CM_COMPILER_FLAGS_MISC']=x

    # Check if lib dependencies
    if len(lib_deps)>0:
       ii={'cm_run_module_uoa':ini['cfg']['cm_modules']['code'],
           'cm_action':'prepare_env_for_all_codes',
           'code_deps':lib_deps,
           'os_uoa':target_os_uid}
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       cm_ld_flags_misc=''
       if 'CM_LD_FLAGS_MISC' in run_set_env2: cm_ld_flags_misc=run_set_env2['CM_LD_FLAGS_MISC']

       for x in r['lib_paths']:
           cm_ld_flags_misc+=' '+x

       run_set_env2['CM_LD_FLAGS_MISC']=cm_ld_flags_misc

    if vrb=='yes':
       cm_kernel.print_for_con('')
       cm_kernel.print_for_con('run_set_env2:')
       cm_kernel.print_for_con(json.dumps(run_set_env2, indent=2))

    # Call code.run to build "code.source" and install to "code" if needed
    ii={}
    ii.update(i)
    ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['code']
    ii['cm_action']='run'
    ii['run_set_env2']=run_set_env2
    if target_file!='': 
       if 'run_output_files' not in ii: ii['run_output_files']=[]
       if target_file not in ii['run_output_files']: ii['run_output_files'].append(target_file)

    # Check output
    if i.get('run_cmd_out1','')!='': ii['run_cmd_out1']=i['run_cmd_out1']
    if i.get('run_cmd_out2','')!='': ii['run_cmd_out2']=i['run_cmd_out2']

    sys.stdout.flush()

    # Check if cleaning program before
    if i.get('clean_program','')=='yes':
       ii_copy=copy.deepcopy(ii)
       ii_copy['run_script']=i.get('clean_program_script_name','')
       ii_copy['calming_delay']='0' # calming delay not needed here
       if vrb=='yes': ii['cm_verbose']=vrb
       r=cm_kernel.access(ii_copy)
       if r['cm_return']>0: return r

    sys.stdout.flush()
    calming_delay=ini['cfg'].get('calming_delay','')
    if calming_delay!='' and float(calming_delay)!=0:
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Calming delay: '+calming_delay+' second(s) ...')
       time.sleep(float(calming_delay))

    state_input=ii.copy()

    # Perform Building
    if vrb=='yes': ii['cm_verbose']=vrb
    r=cm_kernel.access(ii)
    state_output=r.copy()
    if r['cm_return']>0: return r

    rr={}
    rr.update(r)
    rr['target_file']=target_file

    if r.get('run_time_by_module','')!='':
       if vrb=='yes':
          cm_kernel.print_for_con("")
          cm_kernel.print_for_con('Build time: '+r['run_time_by_module'])

    if i.get('ignore_script_error','')!='yes' and ('exit_code' not in r or r['exit_code']!=0):
       return {'cm_return':16, 'cm_error':'build failed: script returned non-zero code ('+str(r.get('exit_code',''))+')'}

    # Check binary size
    size=0
    fail=False
    if i.get('skip_target_file_check','')!='yes' and target_file!='':
       if vrb=='yes':
          cm_kernel.print_for_con('')
       p=os.path.join(r['work_dir'], target_file)
       if not os.path.isfile(p):
          if vrb=='yes':
             cm_kernel.print_for_con('Target file ('+p+') was not found - likely problem with compilation')
          fail=True
       else:
          size=os.path.getsize(p);
          rr['target_file_size']=str(size)
          if vrb=='yes':
             cm_kernel.print_for_con('Target file size:  '+rr['target_file_size'])

    # Finish installation if set up
    if install and not fail:
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Copying script to the cM bin directory ...')

       p1=os.path.join(cm_kernel.ini[cm_kernel.env_cm_bin], script_filename)
       try:
          shutil.copyfile(script_name, p1)
       except Exception as e:
          return {'cm_return':1, 'cm_error':'error while copying script to cM bin directory ('+format(e)+')'}

       if 'set_executable' in target_os_cfg:
          r=os.system(target_os_cfg['set_executable']+' '+p1)

       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Updating code entry (successful installation) ...')
          cm_kernel.print_for_con('')

       data={'build_finished_successfully':'yes'}
       if 'add_to_code' in work_cfg: data.update(work_cfg['add_to_code'])

       data['state_input']=state_input
       data['state_output']=state_output

       ii={'cm_run_module_uoa':install_module_uoa,
           'cm_action':'update',
           'cm_array':data,
           'cm_data_uoa':install_uid}
       if install_repo_uoa!='': ii['cm_repo_uoa']=install_repo_uoa
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

    if not fail:
       if vrb=='yes':
          cm_kernel.print_for_con('')
          cm_kernel.print_for_con('Building finished successfully!')

    return rr

# ============================================================================
def web_build(i):

    """
    Build program through web

    Input:  See build(i)
    Output: See build(i)

    """

    # Get web style
    if 'cfg' in cm_kernel.ini['web_style']: web=cm_kernel.ini['web_style']['cfg']
    else:
       return {'cm_return':1, 'cm_error':'web style is not defined'}

    cm_kernel.print_for_con('<span class="cm-title">Build and run program</span><br>')

    # Detecting/restoring data from forms
    a1={}
    r=cm_kernel.access({'cm_run_module_uoa':ini['cfg']['cm_modules']['cm-web'],
                        'cm_action':'detect_form_params',
                        'cm_array':i, 
                        'cm_prefix':'#form1'})
    if r['cm_return']>0: return r
    cm_form_array1=r['cm_array']
    cm_form_commands1=r['cm_commands']

    # Get data description for this action
    r=cm_kernel.get_data_description({'cm_module_uoa':ini['cm_module_uoa'], 
                                      'cm_which_action':i['cm_action']})
    if r['cm_return']>0: return r
    cm_data_desc1=r['cm_data_desc']
    cm_params_default1=r['cm_params_default']

    # Check default
    forms_exists='yes'
    if len(cm_form_array1)==0:
       a1=cm_params_default1

       forms_exists='no'
    else:
       r=cm_kernel.restore_flattened_array({'cm_array':cm_form_array1, 
                                            'cm_replace_in_keys':{'^35^':'#', '^64^':'@'}})
       if r['cm_return']>0: return r
       a1=r['cm_array']

    # Set common parameters
    last_command={}

    ii={}
    ii['work_dir_repo_uoa']=a1.get('work_dir_repo_uoa','')
    ii['ctuning_setup_uoa']=a1.get('ctuning_setup_uoa','')
    ii['work_dir_module_uoa']=ini['cm_module_uid']
    ii['work_dir_data_uoa']=a1.get('work_dir_data_uoa','')
    ii['run_host_os_uoa']=a1.get('run_host_os_uoa','')
    ii['run_target_processor_uoa']=a1.get('run_target_processor_uoa','')
    ii['cm_detach_console']='yes'
    if 'install_data_uid' in a1 and a1['install_data_uid']!='': ii['install_data_uid']=a1['install_data_uid']
    if 'install_data_display_as_alias' in i: ii['install_data_display_as_alias']=i['install_data_display_as_alias']
    if 'keep_all_files' in a1 and a1['keep_all_files']!='': ii['keep_all_files']=a1['keep_all_files']

    # Check if build
    if 'cm_submit_build' in i:
       ii['cm_run_module_uoa']=ini['cm_module_uoa']
       ii['cm_action']='build'

       ii['build_target_os_uoa']=a1.get('build_target_os_uoa','')
       ii['work_dir_module_uoa']=ini['cm_module_uid']
       ii['run_script_uoa']=a1.get('build_run_script_uoa')
       ii['run_script']=a1.get('build_run_script')

       ii['code_deps']=[]
       ii['run_set_env2']={}

       flags=''
       if a1.get('compiler_flags','')!='': flags=a1['compiler_flags']
       if a1.get('compiler_flags_node',{}).get('all_compiler_flags',{}).get('base_flag','')!='': 
          flags=a1['compiler_flags_node']['all_compiler_flags']['base_flag']+' '+flags

       if a1.get('compiler_code_uoa','')!='': ii['code_deps'].append({"CM_CODE_DEP_COMPILER":a1['compiler_code_uoa']})
       if len(a1.get('cm_dependencies',[]))>0: ii['cm_dependencies']=a1['cm_dependencies']
       if flags!='': ii['run_set_env2']['CM_COMPILER_FLAGS_CC_OPTS']=flags
       if a1.get('compilation_type','')!='': ii['compilation_type']=a1['compilation_type']

       if a1.get('install','')=='yes': ii['install']='yes'
       if a1.get('install_data_uid','')=='yes': ii['install_data_uid']=a1['install_data_uid']
       if a1.get('install_repo_uoa','')!='': ii['install_repo_uoa']=a1['install_repo_uoa']

       if a1.get('clean_program','')!='': ii['clean_program']=a1['clean_program']
       if a1.get('clean_program_script_name','')!='': ii['clean_program_script_name']=a1['clean_program_script_name']

       if 'add_to_code_entry' in i: ii['add_to_code_entry']=i['add_to_code_entry']
       if 'add_rem_to_script' in i: ii['add_rem_to_script']=i['add_rem_to_script']

       last_command=ii

       r=cm_kernel.access_fe_through_cmd(ii)
       if r['cm_return']>0: return r

       del(i['cm_submit_build'])

    # Check if run
    elif 'cm_submit_run' in i:
       ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['code']
       ii['cm_action']='run'

       ii['run_target_os_uoa']=a1.get('build_target_os_uoa','')
       ii['run_cmd_key']=a1.get('run_cmd_key')
       ii['dataset_uoa']=a1.get('dataset_uoa')

       ii['run_set_env2']={}
       if a1.get('repeat_kernel','')!='': ii['run_set_env2']['CT_REPEAT_MAIN']=a1['repeat_kernel']

       last_command=ii

       r=cm_kernel.access_fe_through_cmd(ii)
       if r['cm_return']>0: return r

       del(i['cm_submit_run'])


    # Always redrawweb form
    # Check if setup is selected and prune choices *********************************************************************
    cm_scen_c=''
    cm_scen_p=''

    cm_setup_uoa=a1.get('ctuning_setup_uoa','')
    if cm_setup_uoa!='':
       # Load setup
       ii={}
       ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['ctuning.setup']
       ii['cm_action']='load'
       ii['cm_data_uoa']=cm_setup_uoa
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       ds=r['cm_data_obj']['cfg']

       cm_host_os_uoa_list=ds.get('cm_host_os_uoa_list',[])
       if len(cm_host_os_uoa_list)>0: cm_data_desc['##package_host_os_uoa']['choice']=cm_host_os_uoa_list

       cm_target_os_uoa_list=ds.get('cm_target_os_uoa_list',[])
       if len(cm_target_os_uoa_list)>0: cm_data_desc['##build_target_os_uoa']['choice']=cm_target_os_uoa_list

       run_target_processor_uoa_list=ds.get('run_target_processor_uoa_list',[])
       if len(run_target_processor_uoa_list)>0: cm_data_desc['##run_target_processor_uoa']['choice']=run_target_processor_uoa_list

       # Check class
       ctuning_scenario_uoa=ds.get('ctuning_scenario_uoa','')
       if ctuning_scenario_uoa!='':
          ii={}
          ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['ctuning.scenario']
          ii['cm_action']='load'
          ii['cm_data_uoa']=ctuning_scenario_uoa
          r=cm_kernel.access(ii)
          if r['cm_return']>0: return r
          ds1=r['cm_data_obj']['cfg']

          cm_scen_c=ds1.get('cm_classes_uoa',[])
          cm_scen_p=ds1.get('cm_properties',{})

    # This table is used to show json in the right corner
    cm_kernel.print_for_con('<br><table border="0"><tr>')

    cm_kernel.print_for_con('<td align="center">')
    cm_kernel.print_for_con('<FORM ACTION="" name="add_edit" METHOD="POST" enctype="multipart/form-data" accept-charset="utf-8">' )

    ii={'cm_run_module_uoa':ini['cfg']['cm_modules']['cm-web'],
        'cm_action':'visualize_data',
        'cm_array':a1,
        'cm_data_desc':cm_data_desc1,
        'cm_form_commands':cm_form_commands1,
        'cm_separator':'#',
        'cm_separator_form':'#form1#',
        'cm_forms_exists':forms_exists,
        'cm_support_raw_edit':'no',
        'cm_mode':'add'}
    if 'cm_raw_edit' in i: ii['cm_raw_edit']=i['cm_raw_edit']
    if 'cm_back_json' in i: ii['cm_back_json']=i['cm_back_json']
    r=cm_kernel.access(ii)
    if r['cm_return']>0: return r
    cm_kernel.print_for_web(r['cm_string'])

    cm_kernel.print_for_con('<input type="submit" class="cm-button" name="cm_submit_build" value="Build">')
    cm_kernel.print_for_con('<input type="submit" class="cm-button" name="cm_submit_run" value="Run">')

    # Pruning vars

    cm_t_os_uoa=a1.get('build_target_os_uoa','')
    cm_h_os_uoa=a1.get('package_host_os_uoa','')
    cm_p_uoa=a1.get('run_target_processor_uoa','')
    cm_repo_uoa=a1.get('package_repo_uoa','')

    # Check target OS classes and properties
    cm_t_os_c=''
    cm_t_os_p=''
    if cm_t_os_uoa!='':
       ii={}
       ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['os']
       ii['cm_action']='load'
       ii['cm_data_uoa']=cm_t_os_uoa
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       cm_t_os_uid=r['cm_uid']
       cm_t_os_uoa=r['cm_uoa']

       d=r['cm_data_obj']['cfg']

       cm_t_os_c=d.get('cm_classes_uoa',[])
       cm_t_os_p=d.get('cm_properties',{})

    cm_h_os_c=''
    cm_h_os_p=''
    cm_h_os_cfg={}
    if cm_h_os_uoa!='':
       ii={}
       ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['os']
       ii['cm_action']='load'
       ii['cm_data_uoa']=cm_h_os_uoa
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       cm_h_os_uid=r['cm_uid']
       cm_h_os_uoa=r['cm_uoa']
       cm_h_os_cfg=r['cm_data_obj']['cfg']

       d=cm_h_os_cfg
       cm_h_os_c=d.get('cm_classes_uoa',[])
       cm_h_os_p=d.get('cm_properties',{})

    cm_p_c=''
    cm_p_p=''
    if cm_p_uoa!='':
       ii={}
       ii['cm_run_module_uoa']=ini['cfg']['cm_modules']['processor']
       ii['cm_action']='load'
       ii['cm_data_uoa']=cm_p_uoa
       r=cm_kernel.access(ii)
       if r['cm_return']>0: return r

       cm_p_uid=r['cm_uid']
       cm_p_uoa=r['cm_uoa']

       d=r['cm_data_obj']['cfg']

       cm_p_c=d.get('cm_classes_uoa',[])
       cm_p_p=d.get('cm_properties',{})

    cm_kernel.print_for_con('<br>')
    cm_kernel.print_for_con('<BR>')
    cm_kernel.print_for_con('<input type="submit" class="cm-button" value="Refresh">')

    cm_kernel.print_for_con('</FORM><br>')
    cm_kernel.print_for_con('</td>')
    cm_kernel.print_for_con('<td valign="TOP">')
 
    # Debug/developer mode
    if a1.get('cm_show_json','')=='yes':
       cm_kernel.print_for_web('<div class="cm-round-div" align="left">')
       cm_kernel.print_for_con('<i><B><small>JSON to reproduce last command</small></B></i>')
       cm_kernel.print_for_con('<HR class="cm-hr">')

       if 'cm_detach_console' in last_command: del(last_command['cm_detach_console'])
       cm_kernel.print_for_web(json.dumps(last_command, indent=2).replace('\n','\n<BR>\n'))

       if last_command.get('cm_run_module_uoa','')!='':
          cm_kernel.print_for_con('<HR class="cm-hr">')
          cm_kernel.print_for_con('<b>Envoke command from CMD:</b><BR>')
          cm_kernel.print_for_con('<i>cm '+last_command['cm_run_module_uoa']+' @input.json</i>')

       cm_kernel.print_for_web('</div>')

    cm_kernel.print_for_con('</td></tr></table>')

    return {'cm_return':0}
