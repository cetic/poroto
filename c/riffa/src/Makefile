RIFFADIR=.

CPPFLAGS=-g -I$(RIFFADIR)/include -I.
CFLAGS=-std=c99
LDFLAGS=-lriffa

test: riffa.o c_wrapper.o tb.o
	$(CXX) $(LDFLAGS) -o $@ $^

clean:
	rm -f *.o test
