prefix=/usr/local

all:
	gcc -march=native -O3 -o debayer debayerstandalone.c -L. -lcfitsio -lm
	# -I/usr/include/python3.3


debug:
	gcc -march=native -g -O0 -o debayer debayerstandalone.c -L. -lcfitsio -lm


install:
	install -m 0755 debayer $(prefix)/bin
