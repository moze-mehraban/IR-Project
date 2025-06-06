def gamma_decode(bitstring):
    i = 0
    numbers = []
    while i < len(bitstring):
        # Count leading 1s
        n = 0
        while i < len(bitstring) and bitstring[i] == '1':
            n += 1
            i += 1
        if i >= len(bitstring):
            break
        # Skip the first 0
        i += 1
        # Read offset
        offset = bitstring[i:i+n]
        i += n
        # Build binary number
        num = int('1' + offset, 2) if n > 0 else 1
        numbers.append(num+ (numbers[-1] if numbers else 0))
    return numbers

# Example usage:
print(gamma_decode("1000100")) 