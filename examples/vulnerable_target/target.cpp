#include <cstdint>
#include <cstddef>
#include <iostream>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size > 0 && Data[0] == 'B') {
        // Prevent compiler optimization using volatile
        volatile char *ptr = new char[5];
        ptr[10] = 'X'; // Force out-of-bounds write
        delete[] ptr;
    }
    return 0;
}