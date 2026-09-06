import unittest
from fractions import Fraction
import random
import sys
from tupper_formula import *
from tupper_formula.core import MAX_CELLS, MAX_DECIMAL_DIGITS

A = Bitmap(("010", "101", "111", "101", "101"))

class CoreTests(unittest.TestCase):
    def test_a_known_integer(self):
        self.assertEqual(encode(A), (16015, 80075))
        self.assertEqual(decode(80075, 3, 5), A)

    def test_every_cell_of_a(self):
        for i in range(3):
            for j in range(5):
                self.assertEqual(evaluate(i, 80075+j, 5), int(A.rows[4-j][i]))

    def test_all_small_bitmaps(self):
        for w, h in ((1, 1), (2, 2), (3, 2), (2, 3), (3, 3)):
            for n in range(1 << (w*h)):
                self.assertEqual(encode(decode(h*n, w, h)), (n, h*n))

    def test_asymmetric_orientation(self):
        a = Bitmap(("10010", "01000", "00101"))
        self.assertEqual(a.display_rows("historical"), ("10100", "00010", "01001"))
        self.assertEqual(encode(decode(encode(a)[1], 5, 3)), encode(a))

    def test_fractional_points(self):
        rng = random.Random(20260906)
        for _ in range(1000):
            h = rng.randint(1, 12)
            x = Fraction(rng.randint(0, 120), 8)
            y = Fraction(rng.randint(0, 200000), 16)
            self.assertEqual(evaluate(x,y,h), evaluate_literal(x,y,h))

    def test_enormous_rational_coordinates(self):
        k = 17*((1 << 1800) + 1234567)
        for i,j in ((0,0),(45,8),(105,15)):
            x, y = Fraction(2*i+1,2), Fraction(2*(k+j)+1,2)
            self.assertEqual(evaluate(x,y,17), evaluate_literal(x,y,17))

    def test_boundaries_belong_to_right_or_upper_cell(self):
        # 2 columns, bottom bits 1 and 0; top bits 0 and 1.
        b = Bitmap(("01","10")); _, k = encode(b)
        self.assertEqual(evaluate(Fraction(999,1000),k,2),1)
        self.assertEqual(evaluate(1,k,2),0)
        self.assertEqual(evaluate(0,k+1,2),0)
        self.assertEqual(evaluate(0,k+2,2), evaluate_literal(0,k+2,2))

    def test_repeated_window(self):
        for t in (0,1,7,100):
            self.assertEqual(decode(repeat_k(80075,3,5,t),3,5),A)

    def test_leading_zeros_need_dimensions(self):
        a = Bitmap(("0000","1000"))
        n,k=encode(a)
        self.assertEqual(n,1)
        self.assertEqual(decode(k,4,2),a)
        self.assertNotEqual(decode(k,1,2).width,a.width)

    def test_zero_image(self):
        self.assertEqual(encode(Bitmap(("00","00"))), (0,0))

    def test_reject_invalid_bitmaps(self):
        for rows in ((),("",),("01","0"),("02",),(1,),"010",None):
            with self.subTest(rows=rows), self.assertRaises((ValueError,TypeError)):
                Bitmap(rows)

    def test_reject_invalid_dimensions(self):
        for args in ((0,0,1),(0,1,0),(0,True,1),(0,4097,1),(0,512,512)):
            with self.assertRaises((ValueError,TypeError)):
                decode(*args)

    def test_misalignment(self):
        with self.assertRaises(ValueError): decode(80076,3,5)

    def test_reject_float_bool_and_negative_coordinates(self):
        for x,y in ((0.5,0),(0,1.0),(True,0),(-1,1),(0,-1)):
            with self.assertRaises((TypeError,ValueError)): evaluate(x,y,5)

    def test_decimal_beyond_default_limit(self):
        limit=sys.get_int_max_str_digits()
        text="9"*10000
        self.assertEqual(decimal_string(parse_decimal(text)),text)
        self.assertEqual(sys.get_int_max_str_digits(),limit)

    def test_decimal_chunks(self):
        for n in (0,1,10**9,10**9+1,10**18+123,2**1802):
            self.assertEqual(parse_decimal(decimal_string(n)),n)

    def test_decimal_invalid(self):
        for text in ("", "-1", "1e3", "1 2", "１２", "1"*(MAX_DECIMAL_DIGITS+1),None):
            with self.assertRaises((ValueError,TypeError)):parse_decimal(text)

    def test_formula_variants(self):
        self.assertIn("17",formula_latex(17))
        self.assertIn("32",formula_latex(32,"bit"))
        with self.assertRaises(ValueError): formula_latex(17,"arbitrary")

    def test_immutable(self):
        rows=["01","10"]
        b=Bitmap(rows); rows[0]="00"
        self.assertEqual(b.rows,("01","10"))
