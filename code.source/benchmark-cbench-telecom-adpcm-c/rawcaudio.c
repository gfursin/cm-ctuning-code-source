/* testc - Test adpcm coder */

#include "adpcm.h"
#include <stdio.h>
#include <stdlib.h>

struct adpcm_state state;

#define NSAMPLES 1000

char	abuf[NSAMPLES/2];
short	sbuf[NSAMPLES];

int main() {
    long ct_repeat=0;
    long ct_repeat_max=1;
    int ct_return=0;
    int n;

    if (getenv("CT_REPEAT_MAIN")!=NULL) ct_repeat_max=atol(getenv("CT_REPEAT_MAIN"));

    while(1) {
        struct adpcm_state current_state = state;

	n = read(0, sbuf, NSAMPLES*2);
	if ( n < 0 ) {
	    perror("input file");
	    exit(1);
	}
	if ( n == 0 ) break;

        /* loop_wrap */
        for (ct_repeat=0; ct_repeat<ct_repeat_max; ct_repeat++)
        {
	  /* The call to adpcm_coder modifies the state. We need to make a
	     copy of the state and to restore it before each iteration of the
	     kernel to make sure we do not alter the output of the
	     application. */
          state = current_state;
  	  adpcm_coder(sbuf, abuf, n/2, &state);  /* modifies the state */
	}

	write(1, abuf, n/4);
    }
    return 0;
}
