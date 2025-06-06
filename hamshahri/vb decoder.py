def vb_decode(bitstring):
    numbers = []
    n = 0
    i = 0
    while i < len(bitstring):
        byte = bitstring[i:i+8]
        if len(byte) < 8:
            break
        b = int(byte, 2)
        if b >= 128:
            n = n * 128 + (b - 128)
            numbers.append(n+numbers[-1] if numbers else n)
            n = 0
        else:
            n = n * 128 + b
        i += 8
    return numbers

# Example usage:
# Suppose you have a joined code: "1000011010000100" (which is two bytes: 134 and 132)
decoded = vb_decode("1000001010000001100000011000000110000001")
print(decoded)