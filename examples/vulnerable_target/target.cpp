#include <cstdint>
#include <cstddef>
#include <cstring>
#include <iostream>

// Target function simulating an input parser
void parse_input(const uint8_t *data, size_t size) {
    if (size >= 3) {
        // Deliberate bug: Causes a heap-buffer-overflow / crash if input is "BUG"
        if (data[0] == 'B' && data[1] == 'U' && data[2] == 'G') {
            char *ptr = new char[5];
            // Intentional out-of-bounds write
            ptr[10] = 'X'; 
            delete[] ptr;
        }
    }
}

// libFuzzer entry point
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    parse_input(Data, Size);
    return 0;
}