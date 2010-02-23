all: openseal openseal_decoder zipseal zipseal_decoder

openseal: openseal.c
	$(CC) -o openseal openseal.c

openseal_decoder: openseal_decoder.c
	$(CC) -o openseal_decoder openseal_decoder.c

zipseal: zipseal.c
	$(CC) -Wall -o zipseal zipseal.c

zipseal_decoder: zipseal_decoder.c
	$(CC) -Wall -o zipseal_decoder zipseal_decoder.c

clean:
	rm -f openseal openseal_decoder zipseal zipseal_decoder
