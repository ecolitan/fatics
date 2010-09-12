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
 *
 * This is the Win32 version.
 */

#include <winsock2.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/timeb.h>
#include <sys/types.h>
#include <string.h>
#include <assert.h>

#include "zlib.h"
#include "chuffman.h"

#define BSIZE 1024

/* from putty */
struct input_data {
       int len, rd;
       HANDLE do_read, did_read;
       char *buf;
};
static char ibuf[BSIZE];
static DWORD WINAPI stdin_read_thread(void *param) {
    struct input_data *idata = param;
    int n;
    idata->buf = ibuf;
    while (1) {
       /*if (!ReadConsole(GetStdHandle(STD_INPUT_HANDLE),idata->buf + idata->rd,BSIZE - idata->rd,&n,NULL))
       {
           fprintf(stderr, "ReadConsole failed %d\n", GetLastError());
           exit(1);
       }*/
       n=read(0,idata->buf + idata->rd, BSIZE - idata->rd);
       if (n <= 0) {
           fprintf(stderr, "read failed\n");
           exit(1);
       }
       idata->len = n;
       SetEvent(idata->did_read);
       WaitForSingleObject(idata->do_read, INFINITE);
    }

    /* exiting */
    idata->len = 0;
    SetEvent(idata->did_read);

    return 0;
}

void gettimeofday(struct timeval* t,void* timezone)
{       struct _timeb timebuffer;
        _ftime( &timebuffer );
        t->tv_sec=timebuffer.time;
        t->tv_usec=1000*timebuffer.millitm;
}

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

int makeconn(char *hostname, unsigned short port)
{
        int sockfd;
        struct hostent* host_info;
        struct sockaddr_in address;
        int d;
        long host_address;
        sockfd=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
        if(sockfd == INVALID_SOCKET) {
                perror(NULL);
                exit(1);
        }
        host_info=gethostbyname(hostname);
        if (host_info==NULL) {
                fprintf(stderr, "error resolving host: %d\n", WSAGetLastError());
                exit(1);
        }
        memcpy(&host_address,host_info->h_addr,host_info->h_length);
        address.sin_addr.s_addr=host_address;
        address.sin_port=htons(port);
        address.sin_family=AF_INET;
        d = connect(sockfd,(struct sockaddr*)&address,sizeof(address));
        if (d != 0) {
                fprintf(stderr, "error connecting: %d\n", WSAGetLastError());
                exit(1);
        }
        return sockfd;
}

void mysend(int fd,char *buff,int n)
{
        int k, j;
        k = send(fd, buff, n, 0);
        if (k == SOCKET_ERROR) {
                printf("error writing to ICS (%d)\n", WSAGetLastError());
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
                        mysend(fd,ffub,k);
                        for(c++,k=0;c<*rd;c++,k++)
                                buff[k]=buff[c];
                        *rd=k;
                        c=-1;
                }
}

void getfromfics(int fd, char *buff, int *rd)
{
        int n, m, got_g = 0;
        while(*rd > 0) {
                for(n=0; n<*rd && buff[n]!='\r'; n++) {
                        if (buff[n] == '\0' && n >= 3
                                && !strncmp(buff + n - 3, "[G]",3))
                        {
                                char reply[20]="\x2""9";

                                for(n++; n < *rd; n++) {
                                        buff[n-4] = buff[n];
                                }
                                *rd -= 4;

                                n = crypt(reply,2);
                                mysend(fd, reply, n);

                                got_g = 1;
                                break;
                        }
                }
                if (got_g) {
                        got_g = 0;
                        continue;
                }
                if(n<*rd) n++;
                if (write(1, buff, n) != n) {
                        printf("error writing to stdout (%d)\n",
                                WSAGetLastError());
                        exit(1);
                }
                for (m = n; m < *rd; m++) {
                        buff[m - n] = buff[m];
                }
                *rd -= n;
        }
}

int main(int argc, char **argv)
{
        char *hostname;
        int fd, n;
        unsigned short port;
        struct CHuffman ch;
        DWORD threadid;
        WSADATA wsadata;
        WORD winsock_ver;
        struct input_data idata;

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

        winsock_ver = MAKEWORD(2, 0);
        if (WSAStartup(winsock_ver, &wsadata)) {
                fprintf(stderr,"Error initializing winsock\n");
                return 1;
        }

        fd=makeconn(hostname,port);

        idata.did_read = CreateEvent(NULL, FALSE, FALSE, NULL);
        idata.do_read = CreateEvent(NULL, FALSE, FALSE, NULL);
        idata.rd = 0;
        if (!CreateThread(NULL, 0, stdin_read_thread, &idata, 0, &threadid)) {
                fprintf(stderr, "Unable to create input thread\n");
                exit(1);
        }

        SetConsoleMode(GetStdHandle(STD_INPUT_HANDLE), ENABLE_LINE_INPUT);

        for(;;) {
                WSAEVENT sockev, inev;
                HANDLE evlist[2];
                evlist[0] = idata.did_read;
                sockev = WSACreateEvent();
                if (WSAEventSelect(fd, sockev, FD_READ|FD_CLOSE) == SOCKET_ERROR) {
                       fprintf(stderr, "network error\n");
                       exit(1);
                }
                evlist[1] = sockev;

                switch (WaitForMultipleObjects(2, evlist, FALSE, INFINITE)) {
                        case WAIT_OBJECT_0: {
                                /* did_read (from stdin); send to fics */
                                if (idata.len == 0) {
                                        printf("stdin closed\n");
                                        exit(1);
                                        break;
                                }
                                idata.rd += idata.len;
                                sendtofics(fd, idata.buf, &idata.rd);
                                if (idata.rd==BSIZE) {
                                        fprintf(stderr,"Line tooooo long! I die!\n");
                                        exit(1);
                                }

                                /* read some more from stdin */
                                SetEvent(idata.do_read);
                                break;
                        }
                        case WAIT_OBJECT_0 + 1: {
                                /* read from ICS */
                                static int rd = 0;
                                static char buf[BSIZE];
                                static int dec_rd = 0;
                                static char dec_buf[4*BSIZE];
                                int ret;

                                assert(rd == 0);
                                n = recv(fd, buf, BSIZE - rd, 0);
                                if (!n) {
                                        fprintf(stderr,"Connection closed by ICS\n");
                                        exit(0);
                                }
                                if (n == -1) {
                                        fprintf(stderr,"Error reading from ICS\n");
                                        exit(1);
                                }
                                rd += n;

                                /* decompress the data received */
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
                                break;
                        }
                        default:
                                fprintf(stderr, "wait error\n");
                                exit(1);

                }
        }
}

/* vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
 */
