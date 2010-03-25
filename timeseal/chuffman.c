/***************************************************************************
*                  Canonical Huffman Encoding and Decoding
*
*   File    : chuffman.c
*   Purpose : Use canonical huffman coding to compress/decompress files
*   Author  : Michael Dipperstein
*   Date    : November 20, 2002
*
****************************************************************************
*
* Huffman: An ANSI C Canonical Huffman Encoding/Decoding Routine
* Copyright (C) 2002-2005, 2007 by
* Michael Dipperstein (mdipper@alumni.engr.ucsb.edu)
*
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
***************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "huflocal.h"
#include "bitarray.h"
#include "bitfile.h"

/* automatically-generated code table */
#include "codes.c"

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
	canonical_list_t canonicalList[NUM_CHARS];      /* list of canonical codes */
};

int lenIndex[NUM_CHARS]; /* for decoding */

/* creating canonical codes */
static int AssignCanonicalCodes(canonical_list_t *cl);
static int CompareByCodeLen(const void *item1, const void *item2);
static int CompareBySymbolValue(const void *item1, const void *item2);

/* reading/writing code to file */
static int ReadHeader(canonical_list_t *cl);

int CHuffmanInit(struct CHuffman *ch)
{
    int i;
    /* initialize canonical list */
    for (i = 0; i < NUM_CHARS; i++) {
        ch->canonicalList[i].codeLen = 0;
        ch->canonicalList[i].code = NULL;
    }
    
    if (!ReadHeader(ch->canonicalList)) {
        return FALSE;
    }

    /* sort the header by code length */
    qsort(ch->canonicalList, NUM_CHARS, sizeof(canonical_list_t),
        CompareByCodeLen);
    
    if (AssignCanonicalCodes(ch->canonicalList) == 0)
    {
        /* failed to assign codes */
        for (i = 0; i < NUM_CHARS; i++)
        {
            if(ch->canonicalList[i].code != NULL)
            {
                BitArrayDestroy(ch->canonicalList[i].code);
            }
        }

        return FALSE;
    }

    if (ch->for_encode) {
	    /* re-sort list in lexical order for use by encode algorithm */
	    qsort(ch->canonicalList, NUM_CHARS, sizeof(canonical_list_t),
		CompareBySymbolValue);
    }
    else {
		/* decoding */
            	ch->outIndex = 0;
	    /* create an index of first code at each possible length */
	    for (i = 0; i < NUM_CHARS; i++)
	    {
		lenIndex[i] = NUM_CHARS;
	    }

	    for (i = 0; i < NUM_CHARS; i++)
	    {
		if (lenIndex[ch->canonicalList[i].codeLen] > i)
		{
		    /* first occurance of this code length */
		    lenIndex[ch->canonicalList[i].codeLen] = i;
		}
	    }
    }

    return TRUE;
}

int CHuffmanEncode(struct CHuffman *ch)
{
    bit_file_t bfpOut;
    int c, i;


    bfpOut.buf = ch->outBuf;
    bfpOut.bufLen = ch->outLen;
    bfpOut.mode = BF_WRITE;
    BitFileInit(&bfpOut);

    /* read characters from file and write them to encoded file */
    for (i = 0; i < ch->inLen; i++) {
	c = ch->inBuf[i];
        /* write encoded symbols */
        if (BitFilePutBits(&bfpOut,
            BitArrayGetBits(ch->canonicalList[c].code),
            ch->canonicalList[c].codeLen) == EOF)
        {
            fprintf(stderr, "buffer full writing\n");
            exit(1);
        }
    }

    /* now write EOF */
    if (BitFilePutBits(&bfpOut,
        BitArrayGetBits(ch->canonicalList[EOF_CHAR].code),
        ch->canonicalList[EOF_CHAR].codeLen) == EOF)
    {
            fprintf(stderr, "buffer full writing\n");
            exit(1);
    }

    /* clean up */
    BitFileClose(&bfpOut);

    ch->outIndex = bfpOut.bufPos;
    return 0;
}

int CHuffmanDecode(struct CHuffman *ch)
{
    bit_file_t bfpIn;
    bit_array_t *code;
    byte_t length;
    char decodedEOF;
    int i, newBit;

    /* open binary output file and bitfile input file */
    bfpIn.mode = BF_READ;
    bfpIn.buf = ch->inBuf;
    bfpIn.bufLen = ch->inLen;
    BitFileInit(&bfpIn);

    /* allocate canonical code list */
    code = BitArrayCreate(256);
    if (code == NULL)
    {
        perror("Bit array allocation");
        BitFileClose(&bfpIn);
        return FALSE;
    }

    /* now we have a huffman code that matches the code used on the encode */

    /* decode input file */
    length = 0;
    BitArrayClearAll(code);
    decodedEOF = FALSE;

    while (((newBit = BitFileGetBit(&bfpIn)) != EOF) && (!decodedEOF)) {
        if (newBit == BUFFER_EMPTY) {
            return BUFFER_EMPTY;
        }
        if (newBit != 0)
        {
            BitArraySetBit(code, length);
        }

        length++;

        if (lenIndex[length] != NUM_CHARS)
        {
            /* there are code of this length */
            for(i = lenIndex[length];
                (i < NUM_CHARS) && (ch->canonicalList[i].codeLen == length);
                i++)
            {
                if (BitArrayCompare(ch->canonicalList[i].code, code) == 0)
                {
                    /* we just read a symbol output decoded value */
                    if (ch->canonicalList[i].value != EOF_CHAR)
                    {
			if (ch->outIndex >= ch->outLen) {
				/* buffer limit reached */
        			BitFileClose(&bfpIn);
				return FALSE;
			}
			ch->outBuf[ch->outIndex++] = ch->canonicalList[i].value;
                    }
                    else
                    {
                        decodedEOF = TRUE;
                    }

                    BitArrayClearAll(code);
                    length = 0;

                    break;
                }
            }
        }
    }

    /* close all files */
    BitFileClose(&bfpIn);

    return 0;
}

/****************************************************************************
*   Function   : CompareByCodeLen
*   Description: Compare function to be used by qsort for sorting canonical
*                list items by code length.  In the event of equal lengths,
*                the symbol value will be used.
*   Parameters : item1 - pointer canonical list item
*                item2 - pointer canonical list item
*   Effects    : None
*   Returned   : 1 if item1 > item2
*                -1 if item1 < item 2
*                0 if something went wrong (means item1 == item2)
****************************************************************************/
static int CompareByCodeLen(const void *item1, const void *item2)
{
    if (((canonical_list_t *)item1)->codeLen >
        ((canonical_list_t *)item2)->codeLen)
    {
        /* item1 > item2 */
        return 1;
    }
    else if (((canonical_list_t *)item1)->codeLen <
        ((canonical_list_t *)item2)->codeLen)
    {
        /* item1 < item2 */
        return -1;
    }
    else
    {
        /* both have equal code lengths break the tie using value */
        if (((canonical_list_t *)item1)->value >
            ((canonical_list_t *)item2)->value)
        {
            return 1;
        }
        else
        {
            return -1;
        }
    }

    return 0;   /* we should never get here */
}

/****************************************************************************
*   Function   : CompareBySymbolValue
*   Description: Compare function to be used by qsort for sorting canonical
*                list items by symbol value.
*   Parameters : item1 - pointer canonical list item
*                item2 - pointer canonical list item
*   Effects    : None
*   Returned   : 1 if item1 > item2
*                -1 if item1 < item 2
****************************************************************************/
static int CompareBySymbolValue(const void *item1, const void *item2)
{
    if (((canonical_list_t *)item1)->value >
        ((canonical_list_t *)item2)->value)
    {
        /* item1 > item2 */
        return 1;
    }

    /* it must be the case that item1 < item2 */
    return -1;
}

/****************************************************************************
*   Function   : AssignCanonicalCode
*   Description: This function accepts a list of symbols sorted by their
*                code lengths, and assigns a canonical Huffman code to each
*                symbol.
*   Parameters : cl - sorted list of symbols to have code values assigned
*   Effects    : cl stores a list of canonical codes sorted by the length
*                of the code used to encode the symbol.
*   Returned   : TRUE for success, FALSE for failure
****************************************************************************/
static int AssignCanonicalCodes(canonical_list_t *cl)
{
    int i;
    byte_t length;
    bit_array_t *code;

    /* assign the new codes */
    code = BitArrayCreate(256);
    BitArrayClearAll(code);

    length = cl[(NUM_CHARS - 1)].codeLen;

    for(i = (NUM_CHARS - 1); i >= 0; i--)
    {
        /* bail if we hit a zero len code */
        if (cl[i].codeLen == 0)
        {
            break;
        }

        /* adjust code if this length is shorter than the previous */
        if (cl[i].codeLen < length)
        {
            BitArrayShiftRight(code, (length - cl[i].codeLen));
            length = cl[i].codeLen;
        }

        /* assign left justified code */
        if ((cl[i].code = BitArrayDuplicate(code)) == NULL)
        {
            perror("Duplicating code");
            BitArrayDestroy(code);
            return FALSE;
        }

        BitArrayShiftLeft(cl[i].code, 256 - length);

        BitArrayIncrement(code);
    }

    BitArrayDestroy(code);
    return TRUE;
}

/****************************************************************************
*   Function   : ReadHeader
*   Description: This function reads the header information stored by
*                WriteHeader.  If the same algorithm that produced the
*                original tree is used with these counts, an exact copy of
*                the tree will be produced.
*   Parameters : cl - pointer to list of canonical Huffman codes
*                bfp - file to read from
*   Effects    : Code lengths and symbols are read into the canonical list.
*                Total number of symbols encoded is store in totalCount
*   Returned   : TRUE on success, otherwise FALSE.
****************************************************************************/
static int ReadHeader(canonical_list_t *cl)
{
    int i;

    /* read the code length */
    for (i = 0; i < NUM_CHARS; i++)
    {
	cl[i].value = i;
        cl[i].codeLen = (byte_t)code_lens[i];
    }
    return TRUE;
}

int encode(struct CHuffman *ch, char *inBuf, int inBytes)
{
	char outBuf[1024];
	int i;

	ch->inBuf = inBuf;
	ch->inLen = inBytes;
	ch->outBuf = outBuf;
	ch->outLen = sizeof(outBuf);
	CHuffmanEncode(ch);

	printf("bytes[%d] = \"", ch->outIndex);
	for (i = 0; i < ch->outIndex; i++) {
		printf("\\x%02x", (unsigned char)outBuf[i]);
	}
	printf("\";\n");
	return 0;
}

int decode(struct CHuffman *ch, char *inBuf, int inSize)
{
	char outBuf[1024];
	unsigned int outSize;
	int i;

	ch->inBuf = inBuf;
	ch->inLen = inSize;
	ch->outBuf = outBuf;
	ch->outLen = sizeof(outBuf);
	outSize = CHuffmanDecode(ch);
	for (i = 0; i < ch->outIndex; i++)  {
		printf("%c", outBuf[i]);
	}
	return 0;
}

int main(int argc, char *argv[])
{
	if (argc == 2 && !strcmp(argv[1], "encode")) {
                struct CHuffman ch;
                ch.for_encode = 1;
		if (!CHuffmanInit(&ch)) {
			fprintf(stderr, "initialization error\n");
			exit(1);
		}

		char *inBuf;
		int inBytes;

		inBuf = "hello world\nHi, how are you?\n";
        	inBytes = strlen(inBuf) + 1;
		encode(&ch, inBuf, inBytes);
		
		inBuf = "this is yet another test!!!\nbye\n";
        	inBytes = strlen(inBuf) + 1;
		encode(&ch, inBuf, inBytes);
	}
	else if (argc == 2 && !strcmp(argv[1], "decode")) {
                struct CHuffman ch;
                ch.for_encode = 0;
		if (!CHuffmanInit(&ch)) {
			fprintf(stderr, "initialization error\n");
			exit(1);
		}

		char *inBuf;
		int inBytes;

		inBuf = "\x52\x49\xa7\x0c\x2e\x08\x26\xb3\x60\x22\x20\x66\xa4\x02\xf9\xa1\x2c\x64\x0f\x01\x4d\x80\x09\x93\x80";
	        inBytes = 25;
		decode(&ch, inBuf, inBytes);
	        
		inBuf = "\x72\x91\x7f\x17\xe3\x24\xee\x69\x41\xca\x49\x0d\xd2\x7b\x80\x58\x0b\x01\x6d\x8f\x19\x26\xc0\x04\xc9\xc0";
	        inBytes = 26;
		decode(&ch, inBuf, inBytes);
	}
	else {
		printf("Usage: %s [encode|decode]\n", argv[0]);
	}

	return 0;
}

