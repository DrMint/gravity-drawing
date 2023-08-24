gcc -std=c11 generation.c TinyPngOut.c -o prog -lm -pthread 
./prog
rm prog