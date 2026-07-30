#include <cstdint>
#include <cstddef>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size > 0 && Data[0] == 'B') {
        volatile char *ptr = new char[5];
        ptr[10] = 'X'; // Out-of-bounds write (Heap Buffer Overflow)
        delete[] ptr;
    }
    return 0;
}