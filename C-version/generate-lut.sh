gcc -std=c11 generation-lut.c TinyPngOut.c -o prog -lm -pthread 
./prog
rm prog