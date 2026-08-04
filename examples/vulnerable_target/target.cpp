#include <cstdint>
#include <cstddef>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size > 0 && Data[0] == 'B') {
        // Simple Heap Buffer Overflow
        char *ptr = new char[5];
        ptr[10] = 'X'; // Out-of-bounds write
        delete[] ptr;
    }
    return 0;
}