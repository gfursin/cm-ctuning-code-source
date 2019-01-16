/* 
 RTL for codelets from MILEPOST project.

 Generated by Codelet Finder and updated by Grigori Fursin within EU FP6 MILEPOST project
 http://cTuning.org/lab/people/gfursin

 Agreed to be released by CAPS Entreprise as MILEPOST's deliverable.
*/


#include <stdio.h>
#include <stdlib.h>

int __astex_write_message(const char * format, ...)
{
}

int __astex_write_output(const char * format, ...)
{
}

void __astex_exit_on_error(const char * msg, int code, const char * additional_msg)
{
 printf("Error: %s (%u) %s\n", msg, code, additional_msg);
 exit(1);
}

void * __astex_fopen(const char * name, const char * mode)
{
  FILE* f;
  f=fopen(name, mode);
  if (f==NULL)
  {
    printf("Error: can't open file %s\n", name);
    exit(1);
  }

  return f;
}

void * __astex_memalloc(long bytes)
{
 void* b;

 b=malloc(bytes);

 if (b==NULL)
 {
   printf("Error: can't allocate memory\n");
   exit(1);
 }

 return b;
}

void __astex_close_file(void * file)
{
 fclose(file);
}

void __astex_read_from_file(void * dest, long bytes, void * file)
{
 fread(dest, 1, bytes, file);
}

int __astex_getenv_int(const char * var)
{
 char* p;
 int r=1;

 p=getenv(var);
 if (p!=NULL) r=atoi(p);

 return r;
}

void * __astex_start_measure()
{
 printf("Start kernel\n");
}

double __astex_stop_measure(void * _before)
{
 printf("Stop kernel\n");
}
