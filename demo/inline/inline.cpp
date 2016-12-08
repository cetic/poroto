typedef int dummy_t;

void test_explicit(int f, int &o) {
	o = f;
}

inline void test_inline(int g, int &o) {
	test_explicit(g, o);
}

inline int test_inline_ret_deep(int g) {
	return g;
}

inline int test_inline_ret(int g) {
	return test_inline_ret_deep(g);
}

void test(int f, dummy_t & o) {
	int tmp;
	test_explicit(test_inline_ret(f), tmp);
	if ( test_inline_ret(tmp) || test_inline_ret(f) ) {
		test_inline(tmp, o);
	} else {
		test_inline(tmp, o);
	}
}
