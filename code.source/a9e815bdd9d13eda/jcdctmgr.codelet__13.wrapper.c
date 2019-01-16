/* 
 Codelet from MILEPOST project: http://cTuning.org/project-milepost
 Updated by Grigori Fursin to work with Collective Mind Framework

 3 "./jcdctmgr.codelet__13.wrapper.c" 3 4
*/

#include <stdio.h>

int __astex_write_message(const char * format, ...);
int __astex_write_output(const char * format, ...);
void __astex_exit_on_error(const char * msg, int code, const char * additional_msg);
void * __astex_fopen(const char * name, const char * mode);
void * __astex_memalloc(long bytes);
void __astex_close_file(void * file);
void __astex_read_from_file(void * dest, long bytes, void * file);
int __astex_getenv_int(const char * var);
void * __astex_start_measure();
double __astex_stop_measure(void * _before);
typedef short  JCOEF;
typedef JCOEF  JBLOCK[64];
typedef JCOEF  *JCOEFPTR;
typedef int  DCTELEM;
void  astex_codelet__13(JCOEFPTR output_ptr, DCTELEM *divisors, DCTELEM workspace[64]);
int main(int argc, const char **argv)
{
  JCOEFPTR  output_ptr;
  DCTELEM  *divisors;
  DCTELEM  *workspace;
  void * codelet_data_file_descriptor = (void *) 0;

#ifdef OPENME
  openme_init(NULL,NULL,NULL,0);
  openme_callback("PROGRAM_START", NULL);
#endif

  if (argc < 2)
    __astex_exit_on_error("Please specify data file in command-line.", 1, argv[0]);
  codelet_data_file_descriptor = __astex_fopen(argv[1], "rb");
  
  char * output_ptr__region_buffer = (char *) __astex_memalloc(73240);
  __astex_write_message("Reading output_ptr value from %s\n", argv[1]);
  __astex_read_from_file(output_ptr__region_buffer, 73240, codelet_data_file_descriptor);
  output_ptr = (JCOEFPTR ) (output_ptr__region_buffer + 24l);
  char * divisors__region_buffer = (char *) __astex_memalloc(16104);
  __astex_write_message("Reading divisors value from %s\n", argv[1]);
  __astex_read_from_file(divisors__region_buffer, 16104, codelet_data_file_descriptor);
  divisors = (DCTELEM *) (divisors__region_buffer + 6784l);
  char * workspace__region_buffer = (char *) __astex_memalloc(256);
  __astex_write_message("Reading workspace value from %s\n", argv[1]);
  __astex_read_from_file(workspace__region_buffer, 256, codelet_data_file_descriptor);
  workspace = (DCTELEM *) (workspace__region_buffer + 0l);
  void * _astex_timeval_before = __astex_start_measure();
  int _astex_wrap_loop = __astex_getenv_int("CT_REPEAT_MAIN");
  if (! _astex_wrap_loop)
    _astex_wrap_loop = 1;

#ifdef OPENME
  openme_callback("KERNEL_START", NULL);
#endif

  while (_astex_wrap_loop > 0)
  {
    --_astex_wrap_loop;
  astex_codelet__13(output_ptr, divisors, workspace);

  }

#ifdef OPENME
  openme_callback("KERNEL_END", NULL);
#endif

  __astex_write_output("Total time: %lf\n", __astex_stop_measure(_astex_timeval_before));


#ifdef OPENME
  openme_callback("PROGRAM_END", NULL);
#endif

  return 0;
}

