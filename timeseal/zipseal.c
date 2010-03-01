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
#define BSIZE 1024

char hello[]="zipseal|zipseal|Running on an operating system|";

int crypt(char *s,int l)
{
	struct timeval tv;
	s[l++]='\x18';
	gettimeofday(&tv,NULL);
	l+=sprintf(&s[l],"%ld",(tv.tv_sec%10000)*1000+tv.tv_usec/1000);
	s[l++]='\x19';
	//s[l++]='\x00';
	s[l++]='\x0a';
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
	if(host_info==NULL) {
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
	int n,m;
	while(*rd>0) {
		if(!memcmp(buff,"[G]",*rd<4?*rd:4)) {
			if(*rd<4) {
				break;
			}
			else {
				char reply[20]="\x2""9";
				n = crypt(reply,2);
				mywrite(fd, reply, n);
				for(n = 4; n < *rd; n++)
					buff[n-4] = buff[n];
				*rd -= 4;
				continue;
			}
		}
		for(n=0;n<*rd && buff[n]!='\n';n++);
		//for(n=0;n<*rd && buff[n]!='\r';n++);
		if(n<*rd) n++;
		mywrite(1,buff,n);
		for(m=n;m<*rd;m++) {
			buff[m-n]=buff[m];
		}
		*rd-=n;
	}
}

int main(int argc, char **argv)
{
	char *hostname;
	int port,fd,n;
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
	fd=makeconn(hostname,port);
	n=crypt(hello,strlen(hello));
	mywrite(fd,hello,n);
	for(;;) {
		fd_set fds;
		FD_ZERO(&fds);
		FD_SET(0,&fds);
		FD_SET(fd,&fds);
		select(fd+1,&fds,NULL,NULL,NULL);
		if(FD_ISSET(0,&fds)) {
			static int rd=0;
			static char buff[BSIZE];
			rd+=n=read(0,buff+rd,BSIZE-rd);
			if(!n) {
				fprintf(stderr,"Gasp!\n");
				exit(0);
			}
			if(n==-1) {
				perror(NULL);
				exit(1);
			}
			sendtofics(fd,buff,&rd);
			if(rd==BSIZE) {
				fprintf(stderr,"Line tooooo long! I die!\n");
				exit(1);
			}
		}
		if(FD_ISSET(fd,&fds)) {
			static int rd=0;
			static char buff[BSIZE];
			rd+=(n=read(fd,buff+rd,BSIZE-rd));
			//rd+=n=read(fd,buff,BSIZE-rd);
			if(!n) {
				fprintf(stderr,"Connection closed by ICS\n");
				exit(0);
			}
			if(n==-1) {
				perror(NULL);
				exit(1);
			}
			getfromfics(fd,buff,&rd);
			if(rd==BSIZE) {
				fprintf(stderr,"Receive buffer full! Your ICS killed me!\n");
				exit(1);
			}
		}
	}
}

