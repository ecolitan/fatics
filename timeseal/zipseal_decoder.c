/* 
 * zipseal_decoder
 *
 * openseal_decoder has been designed to be used with the open-source
 * chess server "lasker" maintained by Andrew Tridgell (you can find it
 * at chess.samba.org).
 *
 * Eats: timeseal-encoded messages terminated by \n
 * Spits: for each message a line in the form
 *     <timestamp-in-decimal>: <message>\n
 * where, in case of malformed input, <timestamp-in-decimal> is 0 and
 * <message> is the input line.
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 *     Marcello Mamino
 *       m.mamino@sns.it
 *       http://linuz.sns.it/~m2/
 *       vacaboja on FICS
 *
 * modified by Wil Mahan
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>

#define BSIZE 2048

void decrypt(char *s)
{
        char *tmp_time,*tmp_end,*num_end;
        static char tmp[BSIZE];
        // first a consistency check
        // decode the string
        strcpy(tmp, s);
        tmp_time = strrchr(tmp,'\x18');
        if (!tmp_time) goto malformed_message;
        *tmp_time++ = '\0';
        // find the timestamp end
        tmp_end = tmp_time + strlen(tmp_time);
        *tmp_end='\0';
        // check that the timestamp actually is a number
        strtol(tmp_time,&num_end,16);
        if(num_end!=tmp_end) goto malformed_message;
        // assume we have got a valid message, and print it out
        printf("%s: %s\n",tmp_time,tmp);
        return;
        // in case of a malformed message, just output 0: message\n
malformed_message:
        printf("0: %s\n",s);
        return;
}

int main()
{
        static char buff[BSIZE];
        static char inbuf[BUFSIZ];
        static char outbuf[BUFSIZ];
        if(setvbuf(stdin,inbuf,_IOLBF,BUFSIZ)) return 1;
        if(setvbuf(stdout,outbuf,_IOLBF,BUFSIZ)) return 1;
        while(fgets(buff,BSIZE,stdin)) {
                int l=strlen(buff);
                if(!l || buff[l-1]!='\n') return 1;
                buff[l-1]=0;
                decrypt(buff);
        }
        return 0;
}
