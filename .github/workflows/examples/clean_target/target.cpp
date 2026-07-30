#include <cstdint>
#include <cstddef>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Clean target: Safely parses inputs without memory corruption
    if (Size >= 4 && Data[0] == 'S' && Data[1] == 'A' && Data[2] == 'F' && Data[3] == 'E') {
        // Safe operation
        int x = 42;
        (void)x;
    }
    return 0;
}