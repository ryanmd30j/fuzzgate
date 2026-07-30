#include <cstdint>
#include <cstddef>
#include <cstring>
#include <iostream>

void parse_input(const uint8_t *data, size_t size) {
    if (size >= 1) {
        // Triggers as soon as a seed contains 'B'
        if (data[0] == 'B') {
            char *ptr = new char[5];
            ptr[10] = 'X'; // Out-of-bounds write (Heap Buffer Overflow)
            delete[] ptr;
        }
    }
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    parse_input(Data, Size);
    return 0;
}