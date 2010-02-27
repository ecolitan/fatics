/* 
 * OPENSEAL --- An open-source replacement for timeseal
 * ported to win32 and updated for timeseal2 by Wil Mahan
 * <wmahan at gmail.com>
 *
 * Usage:
 *   openseal ICS-host [ICS-port]
 *   e.g.
 *   openseal freechess.org
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 *     Marcello Mamino (vacaboja on FICS)
 */

#include <winsock2.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/timeb.h>
#include <sys/types.h>
#include <string.h>
#define BSIZE 1024

/* thank god for putty */
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
	if (!n || n < 0) {
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

char *key="Timestamp (FICS) v1.0 - programmed by Henrik Gram.";
//char hello[100]="TIMESTAMP|javaboard|Blackdown Java-Linux Team 1.3.1 Linux|";
char hello[100]="TIMESEAL2|openseal|Running on an operating system|";

int crypt(char *s,int l)
{
	int n;
	struct timeval tv;
	s[l++]='\x18';
	gettimeofday(&tv,NULL);
	l+=sprintf(&s[l],"%ld",(tv.tv_sec%10000)*1000+tv.tv_usec/1000);
	s[l++]='\x19';
	for(;l%12;l++)
		s[l]='1';
#define SC(A,B) s[B]^=s[A]^=s[B],s[A]^=s[B]
	for(n=0;n<l;n+=12)
		SC(n,n+11), SC(n+2,n+9), SC(n+4,n+7);
	for(n=0;n<l;n++)
		s[n]=((s[n]|0x80)^key[n%50])-32;
	s[l++]='\x80';
	s[l++]='\x0a';
	return l;
}

int makeconn(char *hostname,int port)
{
	int sockfd;
	struct hostent* host_info;
	struct sockaddr_in address;
        int d;
	long host_address;
	sockfd=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
	if(sockfd==INVALID_SOCKET) {
		fprintf(stderr, "cannot open socket: %d\n", WSAGetLastError());
		exit(1);
	}
	host_info=gethostbyname(hostname);
	if(host_info==NULL) {
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
            exit(-1);
        }
	return sockfd;
}

void mywrite(int fd,char *buff,int n)
{
	int k, j;
	k = send(fd,buff,n,0);
	if (k==SOCKET_ERROR) {
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
			/*if (c >= 1 && buff[c - 1] == '\r') {
				printf("now got return, c %d\n", c);

				exit(1);
			}*/
			/*if (c < 1 || buff[c - 1] != '\r') {
				printf("FATAL ERROR: c %d, buff-1 %d\n",  c, buff[c - 1]);
				exit(1);
			}*/
			//buff[--c] = '\n';
			memcpy(ffub,buff,c);
			k=crypt(ffub,c);
			mywrite(fd,ffub,k);
			//c++; /* skip newline */
			for(c++,k=0;c<*rd;c++,k++)
				buff[k]=buff[c];
			*rd=k;
			c=-1;
			if (c < -1) {
				printf("FATAL ERROR 2: c %d\n", c);
				exit(1);
			}
		}
}

void getfromfics(int fd, char *buff, int *rd)
{
	static int c=0;
	int n,m,got_g = 0;
	while(*rd>0) {
		for(n=0;n<*rd && buff[n]!='\r';n++) {
			if (buff[n] == '\0' && n >= 3
				&& !strncmp(buff + n - 3, "[G]",3))
			{
				char reply[20]="\x2""9";

				for(n++; n < *rd; n++)
					buff[n-4] = buff[n];
				*rd -= 4;
				
				n = crypt(reply,2);
				mywrite(fd, reply, n);

				got_g = 1;
				break;
			}
                }
		if (got_g) {
			got_g = 0;
			continue;
		}
		if(n<*rd) n++;
		if (write(1,buff,n) != n) {
		        printf("error writing to stdout (%d)\n", WSAGetLastError());
                	exit(1);
                }
		for(m=n;m<*rd;m++)
			buff[m-n]=buff[m];
		*rd-=n;
	}
}

#if 0
		if(!memcmp(buff,"[G]",*rd<4?*rd:4))
			if(*rd<4) break;
			else {
				char reply[20]="\x2""9";
				n = crypt(reply,2);
				mywrite(fd, reply, n);
				for(n = 4; n < *rd; n++)
					buff[n-4] = buff[n];
				*rd -= 4;
				continue;
			}
		//{ int q; printf("\r\n"); for (q = 0; q < *rd; q++) { printf("%d ", buff[q]); } printf("\r\n"); }
		for(n=0;n<*rd && buff[n]!='\r';n++);
		//for(n=0;n<*rd && buff[n]!='\n';n++);
		if(n<*rd) n++;
		if (write(1,buff,n) != n) {
		        printf("error writing to stdout (%d)\n", WSAGetLastError());
                	exit(1);
                }
		for(m=n;m<*rd;m++)
			buff[m-n]=buff[m];
		*rd-=n;
	}
}
#endif

int main(int argc, char **argv)
{
	char *hostname;
	int port,fd,n;
    	DWORD threadid;
    	WSADATA wsadata;
    	WORD winsock_ver;
    	struct input_data idata;
	if(argc==3) {
		hostname=argv[1];
		port=atoi(argv[2]);
	} else if(argc==2) {
		hostname=argv[1];
		port=5000;
	} else {
		fprintf(stderr,"Usage:\n    %s ICS-host [ICS-port]\n",argv[0]);
		return 1;
	}

       	winsock_ver = MAKEWORD(2, 0);
    	if (WSAStartup(winsock_ver, &wsadata)) {
		fprintf(stderr,"Error initializing winsock\n");
		return 1;
	}

	fd=makeconn(hostname,port);

	//printf("\nExperimental timeseal2 for win32 by wmahan -- use at your own risk.\n");

        idata.did_read = CreateEvent(NULL, FALSE, FALSE, NULL);
        idata.do_read = CreateEvent(NULL, FALSE, FALSE, NULL);
	idata.rd = 0;
	if (!CreateThread(NULL, 0, stdin_read_thread, &idata, 0, &threadid)) {
        	fprintf(stderr, "Unable to create input thread\n");
                exit(1);
        }

	n=crypt(hello,strlen(hello));
	mywrite(fd,hello,n);
	
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
				/* did_read */
				if (idata.len == 0) {
					printf("stdin closed\n");
					exit(1);
					break;
				}
				idata.rd+=idata.len;
				sendtofics(fd,idata.buf,&idata.rd);
				if(idata.rd==BSIZE) {
					fprintf(stderr,"Line tooooo long! I die!\n");
					exit(1);
				}
		
				SetEvent(idata.do_read);
				break;
			}
			case WAIT_OBJECT_0 + 1: {
				static int rd=0;
				static char buff[BSIZE];
				rd+=n=recv(fd,buff,BSIZE-rd, 0);
				if(!n) {
					fprintf(stderr,"Connection closed by ICS\n");
					exit(0);
				}
				if(n==-1) {
					fprintf(stderr,"Error reading from ICS\n");
					exit(1);
				}
				getfromfics(fd,buff,&rd);
				if(rd==BSIZE) {
					fprintf(stderr,"Receive buffer full! Your ICS killed me!\n");
					exit(1);
				}
				break;
			}
			default:
				fprintf(stderr,"wait error\n");
				exit(1);
		}
	}
}

