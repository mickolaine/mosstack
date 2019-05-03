prefix=/home/micko/.local

all:
	g++ -march=native -O3 -o raw2fits raw2fits.cpp -L. -lcfitsio -lm -lraw


install:
	install -m 0755 raw2fits $(prefix)/bin
