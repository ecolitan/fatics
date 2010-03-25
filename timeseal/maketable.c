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
* This file is part of the Huffman library.
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
#include "huflocal.h"
#include "bitarray.h"
#include "bitfile.h"

/***************************************************************************
*                            TYPE DEFINITIONS
***************************************************************************/
typedef struct canonical_list_t
{
    short value;        /* characacter represented */
    byte_t codeLen;     /* number of bits used in code (1 - 255) */
    bit_array_t *code;  /* code used for symbol (left justified) */
} canonical_list_t;

/***************************************************************************
*                                CONSTANTS
***************************************************************************/

/***************************************************************************
*                                 MACROS
***************************************************************************/

/***************************************************************************
*                            GLOBAL VARIABLES
***************************************************************************/
canonical_list_t canonicalList[NUM_CHARS];      /* list of canonical codes */

/***************************************************************************
*                               PROTOTYPES
***************************************************************************/
/* creating canonical codes */
static int BuildCanonicalCode(huffman_node_t *ht, canonical_list_t *cl);
static int AssignCanonicalCodes(canonical_list_t *cl);
static int CompareByCodeLen(const void *item1, const void *item2);

/* reading/writing code to file */
static void WriteHeader(canonical_list_t *cl, bit_file_t *bfp);

const char *filename = "fromfics2.txt";
int main(int argc, char *argv[])
{
    FILE *fpIn;
    bit_file_t *bfpOut;
    huffman_node_t *huffmanTree;        /* root of huffman tree */

    /* open binary input file and bitfile output file */
    if ((fpIn = fopen(filename, "rb")) == NULL)
    {
        perror(filename);
        return FALSE;
    }

    bfpOut = MakeBitFile(stdout, BF_WRITE);

    /* build tree */
    if ((huffmanTree = GenerateTreeFromFile(fpIn)) == NULL)
    {
        fclose(fpIn);
        BitFileClose(bfpOut);
        return FALSE;
    }

    /* use tree to generate a canonical code */
    if (!BuildCanonicalCode(huffmanTree, canonicalList))
    {
        fclose(fpIn);
        BitFileClose(bfpOut);
        FreeHuffmanTree(huffmanTree);     /* free allocated memory */
        return FALSE;
    }

    WriteHeader(canonicalList, bfpOut);

    return TRUE;
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
*   Function   : BuildCanonicalCode
*   Description: This function builds a canonical Huffman code from a
*                Huffman tree.
*   Parameters : ht - pointer to root of tree
*                cl - pointer to canonical list
*   Effects    : cl is filled with the canonical codes sorted by the value
*                of the charcter to be encode.
*   Returned   : TRUE for success, FALSE for failure
****************************************************************************/
static int BuildCanonicalCode(huffman_node_t *ht, canonical_list_t *cl)
{
    int i;
    byte_t depth = 0;

    /* initialize list */
    for(i = 0; i < NUM_CHARS; i++)
    {
        cl[i].value = i;
        cl[i].codeLen = 0;
        cl[i].code = NULL;
    }

    /* fill list with code lengths (depth) from tree */
    for(;;)
    {
        /* follow this branch all the way left */
        while (ht->left != NULL)
        {
            ht = ht->left;
            depth++;
        }

        if (ht->value != COMPOSITE_NODE)
        {
            /* handle one symbol trees */
            if (depth == 0)
            {
                depth++;
            }

            /* enter results in list */
            cl[ht->value].codeLen = depth;
        }

        while (ht->parent != NULL)
        {
            if (ht != ht->parent->right)
            {
                /* try the parent's right */
                ht = ht->parent->right;
                break;
            }
            else
            {
                /* parent's right tried, go up one level yet */
                depth--;
                ht = ht->parent;
            }
        }

        if (ht->parent == NULL)
        {
            /* we're at the top with nowhere to go */
            break;
        }
    }

    /* sort by code length */
    qsort(cl, NUM_CHARS, sizeof(canonical_list_t), CompareByCodeLen);

    if (AssignCanonicalCodes(cl))
    {
        /* re-sort list in lexical order for use by encode algorithm */
        qsort(cl, NUM_CHARS, sizeof(canonical_list_t), CompareBySymbolValue);
        return TRUE;    /* success */
    }

    perror("Code assignment failed");
    return FALSE;       /* assignment failed */
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
*   Function   : WriteHeader
*   Description: This function writes the code size for each symbol and the
*                total number of characters in the original file to the
*                specified output file.  If the same algorithm that produced
*                produced the original canonical code is used with these code
*                lengths, an exact copy of the code will be produced.
*   Parameters : cl - pointer to list of canonical Huffman codes
*                bfp - pointer to open binary file to write to.
*   Effects    : Symbol code lengths and symbol count are written to the
*                output file.
*   Returned   : None
****************************************************************************/
static void WriteHeader(canonical_list_t *cl, bit_file_t *bfp)
{
    int i;

    /* write out code size for each symbol */
    printf("/* This file was automatically generated by maketable */\n\n");
    printf("unsigned char code_lens[%d] = {", NUM_CHARS);
    for (i = 0; i < NUM_CHARS; i++)
    {
	if (i % 16 == 0) {
		printf("\n\t");
	}
        printf("%2d, ", cl[i].codeLen);
    }
    printf("\n};\n");
}

