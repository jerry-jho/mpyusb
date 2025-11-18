def print_bytearray(arr):
    for b in arr:
        ib = int(b)
        if ib < 0:
            ib = ib + 256
        print(f"0x{ib:02X}", end=" ")
    print()
    
