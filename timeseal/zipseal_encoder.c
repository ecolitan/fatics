/* 
 * zipseal_encoder
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>

#include "chuffman.h"

#define BSIZE 2048

int encode(struct CHuffman *ch, char *inBuf, int inBytes)
{
        char outBuf[BSIZE];
        int i;

        ch->inBuf = inBuf;
        ch->inLen = inBytes;
        ch->outBuf = outBuf;
        ch->outLen = sizeof(outBuf);
        CHuffmanEncode(ch);

        printf("%04x", ch->outIndex);
        for (i = 0; i < ch->outIndex; i++) {
                printf("%c", outBuf[i]);
        }
        return 0;
}

struct CHuffman ch;
int main()
{
        static char buf[BSIZE];
        /*static char inbuf[BUFSIZ];
        static char outbuf[BUFSIZ];*/
        int count;
        /*if (setvbuf(stdin,inbuf,_IOLBF,BUFSIZ)) {
                return 1;
        }
        if (setvbuf(stdout,outbuf,_IOLBF,BUFSIZ)) {
                return 1;
        }*/
        setbuf(stdin, NULL);
        setbuf(stdout, NULL);
        ch.for_encode = 1;
        if (!CHuffmanInit(&ch)) {
                fprintf(stderr, "initialization error\n");
                exit(1);
        }
        while (!feof(stdin)) {
                /*if (fread(buf, 1, 4, stdin) != 4) {
                        fprintf(stderr, "read error 1\n");
                        exit(1);
                }*/
                if (fscanf(stdin, "%04x", &count) == EOF) {
                        if (feof(stdin)) {
                                break;
                        }
                        else {
                                fprintf(stderr, "received invalid data\n");
                                exit(1);
                        }
                }

                if (count >= sizeof(buf)) {
                        fprintf(stderr, "shouldn't happen\n");
                        return 1;
                }
                if (fread(buf, 1, count, stdin) != count) {
                        fprintf(stderr, "read error: %d\n", count);
                        return 1;
                }
                encode(&ch, buf, count);
        }
        return 0;
}

