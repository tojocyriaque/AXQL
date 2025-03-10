import struct

# Define the values
int_vars = [4, 5, 6, 7, 8]
float_vars = [1.2, 2.3, 3.4, 4.5]
str_vars = ["str1", "str2", "str3", "str4"]

total_pack = b""
for i in range(4):
    strlen = len(str_vars[i])
    # Use little-endian: prefix format string with '<'
    pack = struct.pack(f"<B I f I {strlen}s", i, int_vars[i], float_vars[i], strlen, str_vars[i].encode("utf-8"))
    total_pack += pack

index = 0
L = len(total_pack)
while index < L:
    # Unpack the index (record number)
    i = struct.unpack_from("<B", total_pack, index)[0]
    index += 1

    # Unpack the integer value
    int_val = struct.unpack_from("<I", total_pack, index)[0]
    index += 4

    # Unpack the float value
    float_val = struct.unpack_from("<f", total_pack, index)[0]
    index += 4

    # Unpack the string length
    strlen_i = struct.unpack_from("<I", total_pack, index)[0]
    index += 4

    # Unpack the string itself
    str_val = struct.unpack_from(f"<{strlen_i}s", total_pack, index)[0].decode("utf-8")
    index += strlen_i

    # Update the lists at the correct index
    int_vars[i] = int_val
    float_vars[i] = float_val
    str_vars[i] = str_val

# Print the unpacked results
print("Integer values:", int_vars[:4])
print("Float values:", float_vars[:4])
print("String values:", str_vars[:4])
