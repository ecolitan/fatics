all: openseal openseal_decoder openseal2 openseal_decoder2

openseal: openseal.c
	$(CC) -o openseal openseal.c

openseal_decoder: openseal_decoder.c
	$(CC) -o openseal_decoder openseal_decoder.c

openseal2: openseal2.c
	$(CC) -Wall -o openseal2 openseal2.c

openseal_decoderw: openseal_decoder2.c
	$(CC) -Wall -o openseal_decoder2 openseal_decoder2.c

clean:
	rm -f openseal openseal_decoder openseal2 openseal_decoder2
