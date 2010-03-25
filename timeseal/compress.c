#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>


int test_deflate(char *str, unsigned char *compr, uLong comprLen)
{
    z_stream c_stream; /* compression stream */
    int err;
    uLong len = (uLong)strlen(str)+1;

    c_stream.zalloc = (alloc_func)0;
    c_stream.zfree = (free_func)0;
    c_stream.opaque = (voidpf)0;

    //err = deflateInit(&c_stream, Z_DEFAULT_COMPRESSION);
    err = deflateInit2(&c_stream, 9, Z_DEFLATED, -15, 8, Z_FIXED); //Z_DEFAULT_STRATEGY);
    if (err != Z_OK) {
    	fprintf(stderr, "deflateInit\n"); 
    }
    
    err = deflateSetDictionary(&c_stream, (Bytef *)"", 0);
    if (err != Z_OK) {
    	fprintf(stderr, "deflateSetDictionary\n"); 
    }

    c_stream.next_in  = (Bytef*)str;
    c_stream.next_out = compr;

    while (c_stream.total_in != len && c_stream.total_out < comprLen) {
        c_stream.avail_in = c_stream.avail_out = 1; /* force small buffers */
        err = deflate(&c_stream, Z_NO_FLUSH);
	if (err != Z_OK) {
	    fprintf(stderr, "deflate\n"); 
	}
    }
    /* Finish the stream, still forcing small buffers: */
    for (;;) {
        c_stream.avail_out = 1;
        err = deflate(&c_stream, Z_FINISH);
        if (err == Z_STREAM_END) break;
	if (err != Z_OK) {
	    fprintf(stderr, "deflate\n"); 
	}
    }

    err = deflateEnd(&c_stream);
    if (err != Z_OK) {
        fprintf(stderr, "deflateEnd\n"); 
    }
    return c_stream.total_out;
}

const char *filename = "fromfics.txt";
int main(int argc, char* argv[])
{
	unsigned char buf[2048];
	char line[1025];
        FILE *f = fopen(filename, "r");
	int total_in = 0, total_out = 0;
	if (!f) {
		perror(filename);
		exit(1);
	}
	while (fgets (line, sizeof(line), f)) {
		total_in += strlen(line);
		int c = test_deflate(line, buf, sizeof(buf));
		printf("%d -> %d\n", strlen(line), c);
		total_out += c;
		total_out += 1;
	}
	fclose(f);
	printf("total_in %d, total_out %d, ratio %.2f%%\n", total_in,
		total_out, 100.0 * total_out / total_in);
	return 0;
}

