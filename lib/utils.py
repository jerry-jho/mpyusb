def print_bytearray(arr):
    for b in arr:
        ib = int(b)
        if ib < 0:
            ib = ib + 256
        print(f"0x{ib:02X}", end=" ")
    print()
    
def is_all_zero(arr):
    if arr is None:
        return True
    for b in arr:
        ib = int(b)
        if ib != 0:
            return False
    return True

def is_equal(arr1, arr2):
    if arr1 is None:
        return False
    if arr2 is None:
        return False
    if len(arr1) != len(arr2):
        return False
    for i in range(len(arr1)):
        if arr1[i] != arr2[i]:
            return False
    return True
