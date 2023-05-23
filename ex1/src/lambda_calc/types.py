"""
Homework 1

Your task:
Implement type checking and type inference for simply-typed lambda calculus.
"""

from lambda_calc.constraints import ConstraintsVisitor
from lambda_calc.rebuild import RebuilderVisitor
from lambda_calc.syntax import LambdaParser, pretty
from lambda_calc.unifier import unify
from lib.adt.tree import Tree, PreorderWalk
from pprint import pprint

def get_constraints(expr: Tree) -> tuple[dict[int, str], dict[str: Tree]]:
    return ConstraintsVisitor()(expr)

def rebuild(expr: Tree, type_vars: dict[int, str], type_results: dict[str: Tree]) -> Tree:
    return RebuilderVisitor()(expr, type_vars, type_results)

def type_inference(expr: Tree) -> tuple[Tree, Tree]:
    """
    Input: an expression.
    Output (tuple):
     * The input expression annotated where every bound variable has a 
       type annotation, and a tree representing the type of the whole expression. (type Tree)
     * If encountered a unification error, raise TypeError('type mismatch')
     * If some types cannot be inferred, raise TypeError('insufficient type annotations')
    """
    type_vars, constraints = get_constraints(expr)
    type_results = unify(type_vars.values(), constraints)

    # print_tree_with_type_vars(expr, type_vars)
    # pprint(constraints)
    # pprint(type_results)

    return (rebuild(expr, type_vars, type_results), type_results['T0'])


def print_tree(expr):
    from lib.adt.tree.viz import dot_print
    dot_print(expr)

def print_tree_with_type_vars(expr, type_vars):
    new_expr = Tree.reconstruct(expr)
    for old, new in zip(PreorderWalk(expr), PreorderWalk(new_expr)):
        if id(old) in type_vars:
            new.root = f'{new.root} ({type_vars[id(old)]})'
    print_tree(new_expr)


if __name__ == '__main__':
    # expr = LambdaParser()(r"""
    # \x. (\plus: nat -> nat -> nat. plus x 2)
    # """)
    # expr = LambdaParser()(r"""
    # let add2 = \x. plus x 2 in
    # \f. succ (f True add2)
    # """)
    expr = LambdaParser()(r"""
    (\plus (lt : nat -> nat -> bool). lt ((\x. plus x x) 3) ((\x. plus 5 x) 9))
    """)
    # print_tree(expr)

    out_tree = LambdaParser()(r"""
    \(plus : nat -> nat -> nat) (lt : nat -> nat -> bool). lt ((\(x : nat). plus x x) 3) ((\(x : nat). plus 5 x) 9)
    """)
    out_result = LambdaParser()(r"""
    \(result : ((nat -> nat -> nat) -> (nat -> nat -> bool) -> bool)). result
    """).subtrees[0].subtrees[1]

    if expr:
        print(">> Valid expression.")
        # print(pretty(expr))
        results = type_inference(expr)
        print(results[0] == out_tree)
        print(results[1] == out_result)
        print(pretty(results[0]))
        print(pretty(results[1]))
        print_tree(results[0])
        print_tree(results[1])
    else:
        print(">> Invalid expression.")
    pass