/***************************************************************************
*                        Bit Stream File Implementation
*
*   File    : bitfile.c
*   Purpose : This file implements a simple library of I/O functions for
*             files that contain data in sizes that aren't integral bytes.
*             An attempt was made to make the functions in this library
*             analogous to functions provided to manipulate byte streams.
*             The functions contained in this library were created with
*             compression algorithms in mind, but may be suited to other
*             applications.
*   Author  : Michael Dipperstein
*   Date    : January 9, 2004
*
****************************************************************************
****************************************************************************
*
* Bitfile: Bit stream File I/O Routines
* Copyright (C) 2004-2007 by Michael Dipperstein (mdipper@cs.ucsb.edu)
*
* This file is part of the bit file library.
*
* The bit file library is free software; you can redistribute it and/or
* modify it under the terms of the GNU Lesser General Public License as
* published by the Free Software Foundation; either version 3 of the
* License, or (at your option) any later version.
*
* The bit file library is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
* General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
***************************************************************************/

#include <stdlib.h>
#include <errno.h>
#include "bitfile.h"

/***************************************************************************
*   Function   : MakeBitFile
*   Description: This function naively wraps a standard file in a
*                bit_file_t structure.  ANSI-C doesn't support file status
*                functions commonly found in other C variants, so the
*                caller must be passed as a parameter.
*   Parameters : stream - pointer to the standard file being wrapped.
*                mode - The mode of the file being wrapped.
*   Effects    : A bit_file_t structure will be created for the stream
*                passed as a parameter.
*   Returned   : Pointer to the bit_file_t structure for the bit file
*                or NULL on failure.  errno will be set for all failure
*                cases.
***************************************************************************/
int BitFileInit(bit_file_t *bf)
{
            /* set structure data */
            bf->bufPos = 0;
            bf->bitBuffer = 0;
            bf->bitCount = 0;
            //bf->endian = DetermineEndianess();

	return 0;
}

/***************************************************************************
*   Function   : BitFileClose
*   Description: This function closes a bit file and frees all associated
*                data.
*   Parameters : stream - pointer to bit file stream being closed
*   Effects    : The specified file will be closed and the file structure
*                will be freed.
*   Returned   : 0 for success or EOF for failure.
***************************************************************************/
int BitFileClose(bit_file_t *stream)
{
    if ((stream->mode == BF_WRITE) || (stream->mode == BF_APPEND))
    {
        /* write out any unwritten bits */
        if (stream->bitCount != 0) {
            if (stream->bufPos >= stream->bufLen) {
                return EOF;
            }
            stream->bitBuffer <<= 8 - (stream->bitCount);
	    stream->buf[stream->bufPos++] = stream->bitBuffer;
        }
    }

    /***********************************************************************
    *  TO DO: Consider writing an additional byte indicating the number of
    *  valid bits (bitCount) in the previous byte.
    ***********************************************************************/

    return 0;
}

/***************************************************************************
*   Function   : BitFileGetBit
*   Description: This function returns the next bit from the file passed as
*                a parameter.  The bit value returned is the msb in the
*                bit buffer.
*   Parameters : stream - pointer to bit file stream to read from
*   Effects    : Reads next bit from bit buffer.  If the buffer is empty,
*                a new byte will be read from the file.
*   Returned   : 0 if bit == 0, 1 if bit == 1, and EOF if operation fails.
***************************************************************************/
int BitFileGetBit(bit_file_t *stream)
{
    int returnValue;

    if (stream->bitCount == 0) {
        /* buffer is empty, read another character */
        if (stream->bufPos >= stream->bufLen) {
            return BUFFER_EMPTY;
        }
        else {
            stream->bitCount = 8;
            stream->bitBuffer = stream->buf[stream->bufPos++];
        }
    }

    /* bit to return is msb in buffer */
    stream->bitCount--;
    returnValue = (stream->bitBuffer) >> (stream->bitCount);

    return returnValue & 0x01;
}

/***************************************************************************
*   Function   : BitFilePutBit
*   Description: This function writes the bit passed as a parameter to the
*                file passed a parameter.
*   Parameters : c - the bit value to be written
*                stream - pointer to bit file stream to write to
*   Effects    : Writes a bit to the bit buffer.  If the buffer has a byte,
*                the buffer is written to the file and cleared.
*   Returned   : On success, the bit value written, otherwise EOF.
***************************************************************************/
int BitFilePutBit(const int c, bit_file_t *stream)
{
    int returnValue = c;
        
    stream->bitCount++;
    stream->bitBuffer <<= 1;

    if (c != 0) {
        stream->bitBuffer |= 1;
    }

    /* write bit buffer if we have 8 bits */
    if (stream->bitCount == 8) {
	    if (stream->bufPos >= stream->bufLen) {
	       return EOF;
	    }
        stream->buf[stream->bufPos++] = stream->bitBuffer;
        /* reset buffer */
        stream->bitCount = 0;
        stream->bitBuffer = 0;
    }

    return returnValue;
}

int BitFilePutBits(bit_file_t *stream, void *bits, const unsigned int count)
{
    unsigned char *bytes, tmp;
    int offset, remaining, returnValue;

    bytes = (unsigned char *)bits;

    offset = 0;
    remaining = count;

    /* write whole bytes */
    while (remaining >= 8)
    {
        returnValue = BitFilePutChar(bytes[offset], stream);

        if (returnValue == EOF) {
            return EOF;
        }

        remaining -= 8;
        offset++;
    }

    if (remaining != 0) {
        /* write remaining bits */
        tmp = bytes[offset];

        while (remaining > 0)
        {
            returnValue = BitFilePutBit((tmp & 0x80), stream);

            if (returnValue == EOF) {
                return EOF;
            }

            tmp <<= 1;
            remaining--;
        }
    }

    return count;
}

int BitFilePutChar(const int c, bit_file_t *stream)
{
    unsigned char tmp;

	if (stream->bufPos >= stream->bufLen) {
	    return EOF;
	}

    if (stream->bitCount == 0) {
        /* we can just put a byte */
        stream->buf[stream->bufPos++] = c;
        return 0;
    }

    /* figure out what to write */
    tmp = ((unsigned char)c) >> (stream->bitCount);
    tmp = tmp | ((stream->bitBuffer) << (8 - stream->bitCount));

    stream->buf[stream->bufPos++] = tmp;
        /* put remaining in buffer. count shouldn't change. */
        stream->bitBuffer = c;

    return 0;
}

int BitFileByteAlign(bit_file_t *stream)
{
    if ((stream->mode == BF_WRITE) || (stream->mode == BF_APPEND))
    {
        /* write out any unwritten bits */
        if (stream->bitCount != 0) {
            if (stream->bufPos >= stream->bufLen) {
                return EOF;
            }
            stream->bitBuffer <<= 8 - (stream->bitCount);
	    stream->buf[stream->bufPos++] = stream->bitBuffer;
        }
    }

    stream->bitBuffer = 0;
    stream->bitCount = 0;

    return 0;
}

