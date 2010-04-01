#include "huflocal.h"
#include "bitarray.h"
#include "bitfile.h"

typedef struct canonical_list_t
{
    short value;        /* characacter represented */
    byte_t codeLen;     /* number of bits used in code (1 - 255) */
    bit_array_t *code;  /* code used for symbol (left justified) */
} canonical_list_t;

struct CHuffman {
	char *inBuf;
	unsigned int inLen;
	char *outBuf;
	unsigned int outLen;
        unsigned int outIndex;
	int for_encode;

	/* internal */
	canonical_list_t canonicalList[NUM_CHARS];      /* list of canonical codes */
	/* for decoding */
	int lenIndex[NUM_CHARS];
    	bit_array_t *code;
    	byte_t decode_length;
	int resume;
};

extern int CHuffmanInit(struct CHuffman *ch);
extern int CHuffmanEncode(struct CHuffman *ch);
int CHuffmanDecode(struct CHuffman *ch);

