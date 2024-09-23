def xor_decrypt(hex_string, key):
    try:
        encrypted_bytes = bytes.fromhex(hex_string)
        extended_key = (key * ((len(encrypted_bytes) // len(key)) + 1))[:len(encrypted_bytes)]
        decrypted_chars = ''.join(chr(b ^ ord(k)) for b, k in zip(encrypted_bytes, extended_key))
        return decrypted_chars
    except Exception as e:
        print(f"Failed to decrypt email: {e}")
        
key = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
hex_string = input("Please enter the encrypted hex string: ")
decrypted = xor_decrypt(hex_string, key)
print("Decrypted:", decrypted)


