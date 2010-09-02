/* 
 * zipseal -- An open-source timeseal
 *
 * Usage:
 *   zipseal ICS-host [ICS-port]
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 *     Marcello Mamino (vacaboja on FICS)
 *
 * Modified by Wil Mahan <wmahan at gmail.com>: support international
 * characters; remove obfuscation; add compression.
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <string.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <unistd.h>
#include <zlib.h>
#include <assert.h>

#include "chuffman.h"

#define BSIZE 1024

//char hello[]="zipseal|zipseal|Running on an operating system|";

static int crypt(char *s,int l)
{
        struct timeval tv;
        gettimeofday(&tv,NULL);
        s[l++]='\x18';
        l += sprintf(&s[l],"%lx\n",(tv.tv_sec%10000)*1000+tv.tv_usec/1000);
        //s[l++]='\x0a';
        return l;
}

int makeconn(char *hostname,int port)
{
        int sockfd;
        struct hostent* host_info;
        struct sockaddr_in address;
        long host_address;
        sockfd=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
        if(sockfd==-1) {
                perror(NULL);
                exit(1);
        }
        host_info=gethostbyname(hostname);
        if (host_info==NULL) {
                perror(NULL);
                exit(1);
        }
        memcpy(&host_address,host_info->h_addr,host_info->h_length);
        address.sin_addr.s_addr=host_address;
        address.sin_port=htons(port);
        address.sin_family=AF_INET;
        if(-1==connect(sockfd,(struct sockaddr*)&address,sizeof(address)));
        return sockfd;
}

void mywrite(int fd,char *buff,int n)
{
        if(write(fd,buff,n)==-1) {
                perror(NULL);
                exit(1);
        }
}

void sendtofics(int fd, char *buff, int *rd)
{
        static int c=0;
        for(;c<*rd;c++)
                if(buff[c]=='\n') {
                        char ffub[BSIZE+20];
                        int k;
                        memcpy(ffub,buff,c);
                        k=crypt(ffub,c);
                        mywrite(fd,ffub,k);
                        for(c++,k=0;c<*rd;c++,k++)
                                buff[k]=buff[c];
                        *rd=k;
                        c=-1;
                }
}

void getfromfics(int fd, char *buff, int *rd)
{
        int n, m;
        while (*rd > 0) {
                if(!memcmp(buff,"[G]",*rd<3?*rd:3)) {
                        if(*rd<3) {
                                break;
                        }
                        else {
                                char reply[20]="\x2""9";
                                n = crypt(reply,2);
                                mywrite(fd, reply, n);
                                for(n = 3; n < *rd; n++)
                                        buff[n-3] = buff[n];
                                *rd -= 3;
                                continue;
                        }
                }
                for(n=0;n<*rd && buff[n]!='\n';n++);
                //for(n=0;n<*rd && buff[n]!='\r';n++);
                if(n<*rd) n++;
                mywrite(1, buff, n);
                for(m = n; m < *rd; m++) {
                        buff[m - n] = buff[m];
                }
                *rd -= n;
        }
}

int main(int argc, char **argv)
{
        char *hostname;
        int port,fd,n;
        struct CHuffman ch;

        if(argc==3) {
                hostname=argv[1];
                port=atoi(argv[2]);
        } else if(argc==2) {
                hostname=argv[1];
                port=5001;
        } else {
                fprintf(stderr, "Usage: %s ICS-host [ICS-port]\n", argv[0]);
                return 1;
        }

                ch.for_encode = 0;
                if (!CHuffmanInit(&ch)) {
                        fprintf(stderr, "initialization error\n");
                        exit(1);
                }

        fd=makeconn(hostname,port);
        for(;;) {
                fd_set fds;
                FD_ZERO(&fds);
                FD_SET(0,&fds);
                FD_SET(fd,&fds);
                select(fd + 1, &fds, NULL, NULL, NULL);
                if(FD_ISSET(0, &fds)) {
                        /* read from stdin */
                        static int rd=0;
                        static char buff[BSIZE];
                        n = read(0, buff + rd, BSIZE - rd);
                        rd += n;
                        if(!n) {
                                fprintf(stderr,"Gasp!\n");
                                exit(0);
                        }
                        if(n==-1) {
                                perror(NULL);
                                exit(1);
                        }
                        sendtofics(fd,buff,&rd);
                        if (rd==BSIZE) {
                                fprintf(stderr,"Line tooooo long! I die!\n");
                                exit(1);
                        }
                }
                if (FD_ISSET(fd, &fds)) {
                        /* read from ICS */
                        static int rd = 0;
                        static char buf[BSIZE];
                        static int dec_rd = 0;
                        static char dec_buf[2*BSIZE];
                        int ret;

                        assert(rd == 0);
                        n = read(fd, buf + rd, sizeof(buf) - rd);
                        rd += n;
                        //printf("read %d, total %d\n", n, rd);
                        if (!n) {
                                fprintf(stderr, "Connection closed by ICS\n");
                                exit(0);
                        }
                        if (n == -1) {
                                perror(NULL);
                                exit(1);
                        }

                        ch.inBuf = buf;
                        ch.inLen = rd;
                        ch.outBuf = dec_buf + dec_rd;
                        ch.outLen = sizeof(dec_buf) - dec_rd;
                        ret = CHuffmanDecode(&ch);
                        dec_rd += ch.outIndex;
                        rd = 0;
                        if (ret == BUFFER_EMPTY) {
                        }
                        else if (ret == 0) {
                        }
                        else {
                                fprintf(stderr, "decode error\n");
                                exit(1);
                        }
                        getfromfics(fd, dec_buf, &dec_rd);
                        if (dec_rd >= sizeof(dec_buf)) {
                                fprintf(stderr, "Buffer full reading from ICS\n");
                                exit(1);
                        }
                }
        }
}

