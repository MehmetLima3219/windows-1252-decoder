# Windows 1252 Decoder

Decode and encode text in the Windows-1252 (CP-1252) character set. Maps all 256 byte values to their Unicode code points.

```python
from windows_1252_decoder import decode, encode

text = decode(b"Hello \x93world\x94 \x96 12\x963")
# 'Hello \u201cworld\u201d \u2013 12\u20133'

back = encode(text)
# b'Hello \x93world\x94 \x96 12\x963'
```

## Why this exists

Some legacy data and tooling emit Windows-1252 bytes. Python's built-in `"cp1252"` codec is close, but its behaviour for the five bytes that Windows-1252 leaves officially undefined (0x81, 0x8D, 0x8F, 0x90, 0x9D) has varied across Python versions and can silently differ. This library fixes one interpretation: each of those bytes maps to the corresponding C1 control code (U+0081, U+008D, U+008F, U+0090, U+009D). The trade-off is fidelity to a specific decoding table over compatibility with Python's shifting codec defaults.

`encode` is the inverse: it accepts exactly the characters that have a Windows-1252 byte and raises `ValueError` for anything else (including U+FFFD). There is no silent `?` substitution, because corrupting data quietly is worse than a loud failure for a codec whose job is fidelity.

## Edge cases

- The five "undefined" bytes are mapped to control codes rather than U+FFFD. If your data uses those bytes as filler, you will get control characters in the output string.
- `encode` rejects characters outside the Windows-1252 repertoire. Strip or replace them before calling if you need lossy conversion.
- `decode` accepts `bytes` and `bytearray`; `encode` accepts `str`. Other types raise `TypeError`.
