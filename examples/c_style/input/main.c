#include "main.h"
#include "support.h"

int main (int argc, char * argv []) {
#if A > 0
    printf("The value A was set to %i\n", A);
    do_something(A, 123);
#else
    printf("An unsupported value of A was set\n");
    do_different(A, 654);
#endif
    return 0;
}
