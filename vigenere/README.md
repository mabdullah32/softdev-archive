# Cybersecurity Lab02-Vigenere

## makefile:

### encode
Print the ciphertext after encoding. All spaces and punctuation are removed.

example:
`make encode ARGS="plaintextfile keyfile"` 

### decode
Print the plaintext after decoding. 

example:
`make decode ARGS="ciphertextfile keyfile"`

### crack
Print the most likely plaintext after decoding it with keys of size 1-12.

example:
`make crack ARGS="ciphertextfile"`

### getkey
Print the most likely key. Keysize 12 will be the maximum size you have to check for. If two keys have the same similarity to english, use the smaller key.

example:
`make getkey ARGS="ciphertextfile"`
    

