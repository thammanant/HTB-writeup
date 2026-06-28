def decrypt(pw):
    key = "dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87"
    pw = pw.strip()
    offset = int(pw[:2])
    encrypted = pw[2:]
    decrypted = ""
    for i in range(0, len(encrypted), 2):
        byte = int(encrypted[i:i+2], 16)
        decrypted += chr(byte ^ ord(key[(offset + i//2) % len(key)]))
    return decrypted


hashes = [
    "0242114B0E143F015F5D1E161713",
    "02375012182C1A1D751618034F36415408"
]

for h in hashes:
    print(f"{h} => {decrypt(h)}")
