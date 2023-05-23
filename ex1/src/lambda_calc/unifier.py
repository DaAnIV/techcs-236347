
from lib.adt.tree import Tree
from typing import  Tuple

def is_concrete_type(t: Tree) -> bool:
    return all(map(lambda x: x[0] != 'T', t.terminals))

class AliasTable:
    def __init__(self):
        self.aliases = {}

    def add_alias(self, var1: str, var2: str):
        if var1 not in self.aliases.keys():
            self.aliases[var1] = {var1, var2}
        if var2 not in self.aliases.keys():
            self.aliases[var2] = {var1, var2}

        s1 = self.aliases[var1]
        s2 = self.aliases[var2]
        new_s = s1.union(s2)
        for var in new_s:
            self.aliases[var] = new_s

    def __getitem__(self, var: str) -> set[str]:
        if var not in self.aliases.keys():
            return {var}
        return self.aliases[var]


class Unifier:
    def __init__(self, cons_list):
        self.cons = cons_list
        self.aliases = AliasTable()
        self.results = {}

    def equal_vars(self, var1: str, var2: str) -> bool:
        return var2 in self.aliases[var1]

    def apply_constraint(self, var: str, new_t: Tree) -> bool:
        if var in new_t.terminals: # circular type
            raise TypeError('Circular dependency')

        if new_t.root[0] == 'T':
            if not self.equal_vars(new_t.root[0], var): # new alias case
                self.aliases.add_alias(var, new_t.root)
                return True
            else:
                return False

        changed = False
        for v, t in self.cons:
            if v in t.terminals: # circular type
                raise TypeError('Circular dependency')
            for l in t.leaves:
                if self.equal_vars(l.root, var):
                    changed = True
                    l.root = new_t.root
                    l.subtrees.clear()
                    l.subtrees.extend([Tree.clone(c) for c in new_t.subtrees])

        if is_concrete_type(new_t): # i.e. t is a concrete type
            self.set_concrete_type(var, new_t)

        return changed

    def set_concrete_type(self, var: str, t: Tree):
        for alias in self.aliases[var]:
            if alias in self.results.keys():
                if self.results[alias] != t: # type mismatch
                    raise TypeError('Type mismatch')
            else:
                self.results[alias] = Tree.clone(t)

    @staticmethod
    def unify_trees(t1: Tree, t2: Tree) -> list[Tuple[str, Tree]]:
        if t1.root == 'id':
            if t2.root == 'id':
                if t1.subtrees[0].root == t2.subtrees[0].root:
                    return []
                else:
                    raise TypeError('Type mismatch')
            elif t2.root == '->': # type mismatch
                raise TypeError('Type mismatch')
            else:
                assert(t2.root[0] == 'T')
                return [(t2.root, t1)]
        elif t1.root[0] == 'T':
            if t2.root[0] == 'T' and t1.root == t2.root:
                return []
            else:
                return [(t1.root, t2)]
        else:
            assert(t1.root == '->')
            if t2.root != '->':
                return Unifier.unify_trees(t2, t1)
            else:
                out1 = Unifier.unify_trees(t1.subtrees[0], t2.subtrees[0])
                out2 = Unifier.unify_trees(t1.subtrees[1], t2.subtrees[1])
                out1.extend(out2)
                return out1

    def get_all_clash_constrains(self) -> list[Tuple[str, Tree]]:
        new_cons = []
        for var1, t1 in self.cons:
            for var2, t2 in self.cons:
                if self.equal_vars(var1, var2) and t1 != t2:
                    new_cons.extend(Unifier.unify_trees(t1, t2))
        new_cons = list(filter(lambda t: t[1].root[0] != 'T' or not self.equal_vars(t[0], t[1].root), new_cons))
        return new_cons

    def __call__(self) -> dict[str: Tree]:
        while True:
            change_flag = False
            alias_cons = list(filter(lambda x: x[1].root[0] == 'T',self.cons))
            for var, t in alias_cons:
                ret = self.apply_constraint(var, t)
                change_flag = change_flag or ret
            self.cons = list(filter(lambda x: x[1].root[0] != 'T', self.cons))

            pass
            concrete_cons = list(filter(lambda x: is_concrete_type(x[1]), self.cons))
            for var, t in concrete_cons:
                ret = self.apply_constraint(var, t)
                change_flag = change_flag or ret
            # self.cons = list(filter(lambda x: not is_concrete_type(x[1]), self.cons))

            pass
            for var, t in self.cons:
                ret = self.apply_constraint(var, t)
                change_flag = change_flag or ret

            pass
            new_cons = self.get_all_clash_constrains()
            if len(new_cons) != 0:
                change_flag = True
                self.cons.extend(new_cons)

            if not change_flag:
                return self.results



def unify(type_vars, constraints: dict[str: list[Tree]]) -> dict[str: Tree]:

    cons_list = []
    for var, l in constraints.items():
        for t in l:
            tmp_t = t
            if type(t) == str:
                tmp_t = Tree(t)
            cons_list.append((var, Tree.clone(tmp_t)))

    unifier = Unifier(cons_list)
    results = unifier()

    for var in type_vars:
        if var not in results.keys(): # var's type was not inferred
            raise TypeError('Insufficient constraints')

    return results


