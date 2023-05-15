
from copy import deepcopy
from adt.tree import Tree
from typing import Tuple

def apply_rule_to_tree(rule: Tuple[str, Tree], tree: Tree):
    if tree.root == 'id' and tree.children[0].root == rule[0]:
        tree.root = rule[1].root
        tree.children.clear()
        tree.children.extend(rule[1].children)
    else:
        for child in tree.children:
            apply_rule_to_tree(rule, child)

def apply_rule_to_pool(rule: Tuple[str, Tree], pool: dict[str: Tree]) -> dict[str: Tree]:
    rules_to_add = []
    for name, tree in pool.items():
        if name == rule[0]:
            rules_to_add.extend(unify_trees(rule[1], tree).items())
        else:
            apply_rule_to_tree(rule, tree)

def unify_trees(t1: Tree, t2: Tree) -> dict[str: Tree]:
    if t1.root == 'id' and t2.root == 'id':
        if (t1.children[0].root == t2.children[0].root):
            return {}
        else:
            return {t1.children[0].root: t2}

    elif t1.root == 'id':
        pass
    elif t2.root == 'id':
        return unify_trees(t2, t1)
    else:
        assert(t1.root == t2.root == '->')
        out1 = unify_trees(t1.children[0], t2.children[0])
        out2 = unify_trees(t1.children[1], t2.children[1])
        for rule in out2.items():
            apply_rule_to_pool(rule, out1)
        return out1

def unify_pools(p1: dict[str: Tree, p2: dict[str: Tree]]) -> dict[str: Tree]:
    pass


def unify(cons: dict[str: Tree]) -> dict[str: Tree]:
    src_pool = cons
    dst_pool = deepcopy(cons)
    while True:
        for rule in src_pool.items():
            apply_rule_to_pool(rule, dst_pool)
        break

    for tree in dst_pool.values():
        for name in tree.terminals():
            if name[0] == 'T':
                raise TypeError('insufficient type annotation')
    return dst_pool


