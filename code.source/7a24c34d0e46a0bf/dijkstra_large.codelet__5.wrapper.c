/* 
 Codelet from MILEPOST project: http://cTuning.org/project-milepost
 Updated by Grigori Fursin to work with Collective Mind Framework

 3 "./dijkstra_large.codelet__5.wrapper.c" 3 4
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
struct _NODE  {
  int  iDist;
  int  iPrev;
} ;
typedef struct _NODE  NODE;
void  astex_codelet__5(int NUM_NODES, NODE *rgnNodes, int __astex_addr__ch[1]);
int main(int argc, const char **argv)
{
  int  NUM_NODES = 5;
  NODE  *rgnNodes;
  int  *__astex_addr__ch;
  void * codelet_data_file_descriptor = (void *) 0;

#ifdef OPENME
  openme_init(NULL,NULL,NULL,0);
  openme_callback("PROGRAM_START", NULL);
#endif

  if (argc < 2)
    __astex_exit_on_error("Please specify data file in command-line.", 1, argv[0]);
  codelet_data_file_descriptor = __astex_fopen(argv[1], "rb");
  
  char * rgnNodes__region_buffer = (char *) __astex_memalloc(48);
  __astex_write_message("Reading rgnNodes value from %s\n", argv[1]);
  __astex_read_from_file(rgnNodes__region_buffer, 48, codelet_data_file_descriptor);
  rgnNodes = (NODE *) (rgnNodes__region_buffer + 0l);
  char * __astex_addr__ch__region_buffer = (char *) __astex_memalloc(4);
  __astex_write_message("Reading __astex_addr__ch value from %s\n", argv[1]);
  __astex_read_from_file(__astex_addr__ch__region_buffer, 4, codelet_data_file_descriptor);
  __astex_addr__ch = (int *) (__astex_addr__ch__region_buffer + 0l);
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
  astex_codelet__5(NUM_NODES, rgnNodes, __astex_addr__ch);

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

