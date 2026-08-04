#include <cstdint>
#include <cstddef>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size > 0 && Data[0] == 'S') {
        volatile int dummy = 1;
        (void)dummy;
    }
    return 0; 
}// Forced hash change for controlled baseline run
