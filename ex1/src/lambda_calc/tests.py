import unittest
import types

from lambda_calc.syntax import LambdaParser
from lambda_calc.types import type_inference

class TestTypes(unittest.TestCase):
    def check_valid(self, expr_str, out_tree_str, out_result_str):
        expr = LambdaParser()(expr_str)
        out_tree = LambdaParser()(out_tree_str)
        out_result = LambdaParser()(r"""\(result : (""" + out_result_str + r""")). result""")

        self.assertTrue(expr, "Failed to parse input expr")
        self.assertTrue(out_tree, "Failed to parse output expr")
        self.assertTrue(out_result, "Failed to parse output type expr")
        out_result = out_result.subtrees[0].subtrees[1]

        results = type_inference(expr)
        self.assertEqual(results[0], out_tree, "Inferred tree is not equal to expected tree")
        self.assertEqual(results[1], out_result, "Inferred type is not equal to expected type")

    def test_valid_one(self):
        expr = r"""(\plus (lt : nat -> nat -> bool). lt ((\x. plus x x) 3) ((\x. plus 5 x) 9))"""
        out_tree = r"""\(plus : nat -> nat -> nat) (lt : nat -> nat -> bool). lt ((\(x : nat). plus x x) 3) ((\(x : nat). plus 5 x) 9)"""
        out_result = r"""(nat -> nat -> nat) -> (nat -> nat -> bool) -> bool"""

        self.check_valid(expr, out_tree, out_result)

    def test_valid_two(self):
        expr = r"""\f g (a : real) (z : unreal). f (g a z) (f 5 a)"""
        out_tree = r"""\(f : nat -> (real -> real)) (g : real -> (unreal -> nat)) (a : real) (z : unreal). f (g a z) (f 5 a)"""
        out_result = r"""(nat -> real -> real) -> (real -> unreal -> nat) -> real -> unreal -> real"""

        self.check_valid(expr, out_tree, out_result)

    def test_valid_three(self):
        expr = r"""(\x. x) 1"""
        out_tree = r"""(\x : nat. x) 1"""
        out_result = r"""nat"""

        self.check_valid(expr, out_tree, out_result)

    def test_valid_four(self):
        expr = r"""\x (plus: nat -> nat -> nat). plus x 2"""
        out_tree = r"""\(x: nat) (plus: nat -> nat -> nat). plus x 2"""
        out_result = r"""nat -> (nat -> nat -> nat) -> nat"""

        self.check_valid(expr, out_tree, out_result)

    def test_valid_five(self):
        expr = r"""let succ:(nat -> nat) = \x.x in \x. succ x"""
        out_tree = r"""let succ:(nat -> nat) = \x: nat.x in \x: nat. succ x"""
        out_result = r"""nat -> nat"""

        self.check_valid(expr, out_tree, out_result)

    def test_type_error_one(self):
        expr = LambdaParser()(r"""\x : int. plus x 2""")

        self.assertTrue(expr, "Failed to parse input expr")

        with self.assertRaises(TypeError) as cm:
            type_inference(expr)

    def test_type_error_two(self):
        expr = LambdaParser()(r"""\x (f : nat -> whatever). f (g 3 x)""")

        self.assertTrue(expr, "Failed to parse input expr")

        with self.assertRaises(TypeError) as cm:
            type_inference(expr)


if __name__ == '__main__':
    unittest.main()