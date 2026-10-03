"""Decode and encode using the Windows-1252 character set.

Windows-1252 is an 8-bit single-byte encoding that covers all 256 code points.
Some legacy tooling treats bytes 0x81, 0x8D, 0x8F, 0x90, and 0x9D as undefined
and maps them to U+0081 etc. when reading. This module maps every byte to the
Unicode code point Windows-1252 actually assigns, and rejects bytes outside
0x00..0xFF so callers see a clean ValueError instead of silent truncation.
"""

from __future__ import annotations

# Windows-1252 maps every byte 0x00..0xFF to a Unicode code point. Bytes
# 0x00..0x7F are identical to ASCII. Bytes 0x80..0x9F differ from Latin-1;
# they correspond to a set of punctuation and symbols. Bytes 0xA0..0xFF match
# Latin-1. We build the full 256-entry table explicitly so there are no gaps.

# The row for 0x80..0x9F is the part that distinguishes Windows-1252 from
# ISO-8859-1. These are the exact Unicode assignments per the WHATWG and
# Unicode Consortium mappings.
_HIGH_RANGE = {
    0x80: 0x20AC,  # EURO SIGN
    0x81: 0x0081,  # undefined in some specs; we map to the control code
    0x82: 0x201A,  # SINGLE LOW-9 QUOTATION MARK
    0x83: 0x0192,  # LATIN SMALL LETTER F WITH HOOK
    0x84: 0x201E,  # DOUBLE LOW-9 QUOTATION MARK
    0x85: 0x2026,  # HORIZONTAL ELLIPSIS
    0x86: 0x2020,  # DAGGER
    0x87: 0x2021,  # DOUBLE DAGGER
    0x88: 0x02C6,  # MODIFIER LETTER CIRCUMFLEX ACCENT
    0x89: 0x2030,  # PER MILLE SIGN
    0x8A: 0x0160,  # LATIN CAPITAL LETTER S WITH CARON
    0x8B: 0x2039,  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    0x8C: 0x0152,  # LATIN CAPITAL LIGATURE OE
    0x8D: 0x008D,  # undefined in some specs; we map to the control code
    0x8E: 0x017D,  # LATIN CAPITAL LETTER Z WITH CARON
    0x8F: 0x008F,  # undefined in some specs; we map to the control code
    0x90: 0x0090,  # undefined in some specs; we map to the control code
    0x91: 0x2018,  # LEFT SINGLE QUOTATION MARK
    0x92: 0x2019,  # RIGHT SINGLE QUOTATION MARK
    0x93: 0x201C,  # LEFT DOUBLE QUOTATION MARK
    0x94: 0x201D,  # RIGHT DOUBLE QUOTATION MARK
    0x95: 0x2022,  # BULLET
    0x96: 0x2013,  # EN DASH
    0x97: 0x2014,  # EM DASH
    0x98: 0x02DC,  # SMALL TILDE
    0x99: 0x2122,  # TRADE MARK SIGN
    0x9A: 0x0161,  # LATIN SMALL LETTER S WITH CARON
    0x9B: 0x203A,  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    0x9C: 0x0153,  # LATIN SMALL LIGATURE OE
    0x9D: 0x009D,  # undefined in some specs; we map to the control code
    0x9E: 0x017E,  # LATIN SMALL LETTER Z WITH CARON
    0x9F: 0x0178,  # LATIN CAPITAL LETTER Y WITH DIAERESIS
}

_DECODER_TABLE = [0] * 256
_ENCODER_TABLE: dict[int, int] = {}

for _b in range(256):
    if _b in _HIGH_RANGE:
        _cp = _HIGH_RANGE[_b]
    else:
        _cp = _b
    _DECODER_TABLE[_b] = _cp
    _ENCODER_TABLE[_cp] = _b

# U+FFFD has no Windows-1252 byte; it is intentionally absent from the encoder
# table so encode() raises a clear error.


def decode(data: bytes) -> str:
    """Decode Windows-1252 bytes into a string.

    Every byte 0x00..0xFF maps to exactly one Unicode code point. Bytes outside
    that range are impossible for a bytes/bytearray argument but a bytearray
    mutation between calls could in principle yield non-byte values; we guard
    by checking element types so the error is informative rather than a cryptic
    IndexError from the table.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(
            f"decode() requires bytes or bytearray, got {type(data).__name__}"
        )
    out: list[str] = []
    append = out.append
    for b in data:
        if not isinstance(b, int) or b < 0 or b > 255:
            raise ValueError(
                f"decode() requires bytes in range 0..255, got {b!r}"
            )
        append(chr(_DECODER_TABLE[b]))
    return "".join(out)


def encode(text: str) -> bytes:
    """Encode a string into Windows-1252 bytes.

    Only characters that have a Windows-1252 code point can be encoded. Any
    other character raises ValueError naming the offending code point. This is
    a deliberate choice: silent replacement (e.g. with '?') would corrupt data
    without warning, which is worse than a loud failure for a codec whose job is
    fidelity to a legacy format.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"encode() requires str, got {type(text).__name__}"
        )
    out = bytearray(len(text))
    for i, ch in enumerate(text):
        cp = ord(ch)
        b = _ENCODER_TABLE.get(cp)
        if b is None:
            raise ValueError(
                f"character U+{cp:04X} has no Windows-1252 encoding"
            )
        out[i] = b
    return bytes(out)
