import unittest

from rope_data_structure_kit import Rope


class TestRope(unittest.TestCase):
    def test_empty_rope(self):
        r = Rope()
        self.assertEqual(len(r), 0)
        self.assertEqual(r.to_string(), "")

    def test_basic_construction(self):
        r = Rope("hello world")
        self.assertEqual(len(r), 11)
        self.assertEqual(r.to_string(), "hello world")

    def test_indexing(self):
        r = Rope("abcdef")
        self.assertEqual(r[0], "a")
        self.assertEqual(r[5], "f")
        with self.assertRaises(IndexError):
            r[6]
        with self.assertRaises(IndexError):
            r[-1]

    def test_index_type_error(self):
        r = Rope("abc")
        with self.assertRaises(TypeError):
            r["a"]

    def test_insert_at_beginning(self):
        r = Rope("world")
        r2 = r.insert(0, "hello ")
        self.assertEqual(r2.to_string(), "hello world")
        self.assertEqual(r.to_string(), "world")  # original unchanged

    def test_insert_at_end(self):
        r = Rope("hello")
        r2 = r.insert(5, " world")
        self.assertEqual(r2.to_string(), "hello world")

    def test_insert_in_middle(self):
        r = Rope("helloworld")
        r2 = r.insert(5, " ")
        self.assertEqual(r2.to_string(), "hello world")

    def test_insert_out_of_range(self):
        r = Rope("abc")
        with self.assertRaises(IndexError):
            r.insert(4, "x")
        with self.assertRaises(IndexError):
            r.insert(-1, "x")

    def test_delete(self):
        r = Rope("hello world")
        r2 = r.delete(5, 11)
        self.assertEqual(r2.to_string(), "hello")
        self.assertEqual(r.to_string(), "hello world")

    def test_delete_middle(self):
        r = Rope("hello, world")
        r2 = r.delete(5, 7)
        self.assertEqual(r2.to_string(), "helloworld")

    def test_delete_entire(self):
        r = Rope("abc")
        r2 = r.delete(0, 3)
        self.assertEqual(r2.to_string(), "")
        self.assertEqual(len(r2), 0)

    def test_delete_invalid_range(self):
        r = Rope("abc")
        with self.assertRaises(IndexError):
            r.delete(2, 1)
        with self.assertRaises(IndexError):
            r.delete(-1, 1)
        with self.assertRaises(IndexError):
            r.delete(0, 4)

    def test_replace(self):
        r = Rope("hello world")
        r2 = r.replace(6, 11, "there")
        self.assertEqual(r2.to_string(), "hello there")

    def test_replace_with_empty(self):
        r = Rope("hello world")
        r2 = r.replace(5, 11, "")
        self.assertEqual(r2.to_string(), "hello")

    def test_replace_invalid_range(self):
        r = Rope("abc")
        with self.assertRaises(IndexError):
            r.replace(2, 1, "x")
        with self.assertRaises(IndexError):
            r.replace(0, 4, "x")

    def test_substring(self):
        r = Rope("hello world")
        self.assertEqual(r.substring(0, 5), "hello")
        self.assertEqual(r.substring(6, 11), "world")
        self.assertEqual(r.substring(5, 5), "")

    def test_substring_invalid_range(self):
        r = Rope("abc")
        with self.assertRaises(IndexError):
            r.substring(2, 1)
        with self.assertRaises(IndexError):
            r.substring(0, 4)

    def test_equality(self):
        a = Rope("abc")
        b = Rope("abc")
        c = Rope("abd")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, "abc")

    def test_repr(self):
        r = Rope("abc")
        self.assertEqual(repr(r), "Rope('abc')")

    def test_large_string(self):
        s = "x" * 1000
        r = Rope(s)
        self.assertEqual(len(r), 1000)
        self.assertEqual(r[999], "x")
        self.assertEqual(r.to_string(), s)

    def test_chunk_boundary(self):
        # Force a leaf boundary at 16 characters.
        s = "a" * 16 + "b" * 16
        r = Rope(s)
        self.assertEqual(r[15], "a")
        self.assertEqual(r[16], "b")
        r2 = r.insert(16, "-")
        self.assertEqual(r2.to_string(), "a" * 16 + "-" + "b" * 16)

    def test_unicode(self):
        s = "héllo wörld"
        r = Rope(s)
        self.assertEqual(len(r), len(s))
        self.assertEqual(r.to_string(), s)
        self.assertEqual(r[1], "é")

    def test_initial_not_string(self):
        with self.assertRaises(TypeError):
            Rope(123)

    def test_insert_text_not_string(self):
        r = Rope("abc")
        with self.assertRaises(TypeError):
            r.insert(1, 123)

    def test_replace_text_not_string(self):
        r = Rope("abc")
        with self.assertRaises(TypeError):
            r.replace(1, 2, 123)


if __name__ == "__main__":
    unittest.main()
