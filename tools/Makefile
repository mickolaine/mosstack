prefix=/usr/local

all:
	gcc -march=native -O3 -o debayer debayer.c -L. -lcfitsio -lm


debug:
	gcc -march=native -g -O0 -o debayer debayer.c -L. -lcfitsio -lm


install:
	install -m 0755 debayer $(prefix)/bin