import unittest

from windows_1252_decoder import decode, encode


class TestDecode(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(decode(b""), "")

    def test_ascii_round_trips(self):
        for b in range(0x00, 0x80):
            self.assertEqual(decode(bytes([b])), chr(b))

    def test_high_range_distinguishes_from_latin1(self):
        # 0x80 is EURO SIGN in Windows-1252, not U+0080 (Latin-1 control).
        self.assertEqual(decode(b"\x80"), "\u20AC")
        self.assertEqual(decode(b"\x99"), "\u2122")
        self.assertEqual(decode(b"\x93"), "\u201C")
        self.assertEqual(decode(b"\x94"), "\u201D")

    def test_undefined_slots_map_to_control_codes(self):
        # We interpret the five "undefined" bytes as their C1 control codes.
        self.assertEqual(decode(b"\x81"), "\u0081")
        self.assertEqual(decode(b"\x8D"), "\u008D")
        self.assertEqual(decode(b"\x8F"), "\u008F")
        self.assertEqual(decode(b"\x90"), "\u0090")
        self.assertEqual(decode(b"\x9D"), "\u009D")

    def test_latin1_upper_range_matches(self):
        # 0xA0..0xFF are identical to Latin-1.
        for b in range(0xA0, 0x100):
            self.assertEqual(decode(bytes([b])), chr(b))

    def test_full_table_covers_all_256(self):
        # No byte should produce an empty or error result.
        result = decode(bytes(range(256)))
        self.assertEqual(len(result), 256)

    def test_bytearray_accepted(self):
        self.assertEqual(decode(bytearray(b"AB")), "AB")

    def test_non_bytes_rejected(self):
        with self.assertRaises(TypeError):
            decode("not bytes")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            decode(None)  # type: ignore[arg-type]

    def test_multibyte_sample_string(self):
        sample = b"Hello \x93world\x94 \x96 12\x963"
        self.assertEqual(decode(sample), "Hello \u201Cworld\u201D \u2013 12\u20133")


class TestEncode(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(encode(""), b"")

    def test_ascii_round_trips(self):
        for b in range(0x00, 0x80):
            self.assertEqual(encode(chr(b)), bytes([b]))

    def test_high_range_symbols(self):
        self.assertEqual(encode("\u20AC"), b"\x80")
        self.assertEqual(encode("\u2122"), b"\x99")

    def test_control_code_slots_round_trip(self):
        for cp in (0x81, 0x8D, 0x8F, 0x90, 0x9D):
            self.assertEqual(encode(chr(cp)), bytes([cp]))

    def test_unmappable_raises(self):
        with self.assertRaises(ValueError):
            encode("\uFFFD")
        with self.assertRaises(ValueError):
            encode("emoji\U0001F600")

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            encode(b"bytes")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            encode(123)  # type: ignore[arg-type]

    def test_sample_round_trip(self):
        original = bytes([0x48, 0x93, 0x94, 0x99, 0xA0, 0xFF])
        self.assertEqual(encode(decode(original)), original)


class TestRoundTrip(unittest.TestCase):
    def test_all_mappable_code_points_round_trip(self):
        # Every byte has a Unicode mapping, and every such mapping encodes back.
        for b in range(256):
            original = bytes([b])
            self.assertEqual(encode(decode(original)), original)


if __name__ == "__main__":
    unittest.main()
