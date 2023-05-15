"""
Homework 1

Your task:
Implement type checking and type inference for simply-typed lambda calculus.
"""

from typing import Any
from lambda_calc.syntax import LambdaParser, pretty
from lambda_calc.stdlib import CONSTANTS
from adt.tree import Tree, Walk, PreorderWalk
import itertools
from pprint import pprint

class ConstraintsVisitor(Walk.Visitor):
    def __init__(self, ) -> None:
        self.constraints = None
        self.type_vars = None
        self.bounded_vars = None

    def type_var(self, node: Tree) -> str:
        return self.type_vars[id(node)]

    def __visit_constraints(self, node: Tree):
        if node.root == 'num':
            self.constraints[self.type_var(node)] = 'nat'
        elif node.root == ':':
            self.constraints[self.type_var(node)] = 'nat'
        elif node.root == '\\':
            self.constraints[self.type_var(node)] = f'{self.type_var(node.subtrees[0])} -> {self.type_var(node.subtrees[1])}'
            self.__visit_constraints(node.subtrees[0])
            for subtree in node.subtrees[:-1]:
                self.bounded_vars[subtree.terminals[0]] = self.type_var(subtree)
            self.__visit_constraints(node.subtrees[-1])
            for subtree in node.subtrees[:-1]:
                self.bounded_vars.pop(subtree.terminals[0])
        elif node.root == '@':
            self.constraints[self.type_var(node.subtrees[0])] = f'{self.type_var(node.subtrees[1])} -> {self.type_var(node)}'
            self.__visit_constraints(node.subtrees[0])
            self.__visit_constraints(node.subtrees[1])
        elif node.root == 'id':
            if node.subtrees[0].root in self.bounded_vars:
                self.constraints[self.type_var(node)] = self.bounded_vars[node.subtrees[0].root]

    def __visit_type_var(self, node: Tree, index: int):
        if node.root == 'num':
            self.type_vars[id(node)] = f'T{index}'
        elif node.root == '\\':
            self.type_vars[id(node)] = f'T{index}'
            for i, subtree in enumerate(node.subtrees):
                self.__visit_type_var(subtree, index + i + 1)
        elif node.root == '@':
            self.type_vars[id(node)] = f'T{index}'
            for i, subtree in enumerate(node.subtrees):
                self.__visit_type_var(subtree, index + i + 1)
        elif node.root == 'id':
            self.type_vars[id(node)] = f'T{index}'

    def __call__(self, node: Tree) -> None:
        self.constraints = {}
        self.type_vars = {}
        self.bounded_vars = {}
        self.__visit_type_var(node, 0)
        self.__visit_constraints(node)


def get_constraints(expr: Tree) -> dict[str: Tree]:
    visitor = ConstraintsVisitor()
    visitor(expr)
    print_tree_with_type_vars(expr, visitor.type_vars)
    pprint(visitor.constraints)

    return {}


def type_inference(expr: Tree) -> tuple[Tree, Tree]:
    """
    Input: an expression.
    Output (tuple):
     * The input expression annotated where every bound variable has a 
       type annotation, and a tree representing the type of the whole expression. (type Tree)
     * If encountered a unification error, raise TypeError('type mismatch')
     * If some types cannot be inferred, raise TypeError('insufficient type annotations')
    """
    constraints = get_constraints(expr)
    return (None, None)


def print_tree_with_type_vars(expr, type_vars):
    expr = Tree.reconstruct(expr)
    for x in PreorderWalk(expr):
        if id(x) in type_vars:
            x.root = f'{x.root} ({type_vars[id(x)]})'
    from lib.adt.tree.viz import dot_print
    dot_print(expr)

if __name__ == '__main__':
    # expr = LambdaParser()(r"""
    # let add2 = \x. plus x 2 in
    # \f. succ (f True add2)
    # """)
    expr = LambdaParser()(r"""
    (\x. plus x 2)
    """)
    
    if expr:
        print(">> Valid expression.")
        # print(pretty(expr))
        print(type_inference(expr))
        # dot_print(type_inference(expr)[0])
    else:
        print(">> Invalid expression.")
