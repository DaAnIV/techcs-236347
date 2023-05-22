from lib.adt.tree.build import TreeAssistant
from lib.adt.tree import Tree, Walk

class ConstraintsVisitor(Walk.Visitor):
    def __init__(self, ) -> None:
        self.index = None
        self.constraints: dict[str, list[Tree]] = None
        self.type_vars = None
        self.bounded_vars = None

    def type_var(self, node: Tree) -> str:
        return self.type_vars[id(node)]
    
    def add_constraint(self, node: Tree, constraint: Tree) -> str:
        if self.type_var(node) not in self.constraints:
            self.constraints[self.type_var(node)] = []
        self.constraints[self.type_var(node)].append(constraint)

    def __visit_constraints(self, node: Tree):
        if node.root == 'num':
            self.add_constraint(node, TreeAssistant.build(('id', ('nat',))))
        elif node.root == ':':
            self.add_constraint(node, node.subtrees[1])
        elif node.root == '\\':
            constraint = TreeAssistant.build(('->', (self.type_var(node.subtrees[0]), self.type_var(node.subtrees[1]))))
            self.add_constraint(node, constraint)
            self.__visit_constraints(node.subtrees[0])
            self.bounded_vars[node.subtrees[0].terminals[0]] = self.type_var(node.subtrees[0])
            self.__visit_constraints(node.subtrees[1])
            self.bounded_vars.pop(node.subtrees[0].terminals[0])
        elif node.root == '@':
            constraint = TreeAssistant.build(('->', (self.type_var(node.subtrees[1]), self.type_var(node))))
            self.add_constraint(node.subtrees[0], constraint)
            self.__visit_constraints(node.subtrees[0])
            self.__visit_constraints(node.subtrees[1])
        elif node.root == 'id':
            if node.subtrees[0].root in self.bounded_vars:
                self.add_constraint(node, Tree(self.bounded_vars[node.subtrees[0].root]))
        elif node.root == 'let_':
            self.add_constraint(node.subtrees[1], self.type_var(node.subtrees[3]))
            self.__visit_constraints(node.subtrees[1])
            self.__visit_constraints(node.subtrees[3])
            self.bounded_vars[node.subtrees[1].terminals[0]] = self.type_var(node.subtrees[3])
            self.__visit_constraints(node.subtrees[5])
            self.bounded_vars.pop(node.subtrees[1].terminals[0])

    def add_type_var(self, node: Tree):
        self.type_vars[id(node)] = f'T{self.index}'
        self.index += 1

    def __visit_type_var(self, node: Tree):
        if node.root == 'num':
            self.add_type_var(node)
        elif node.root == '\\':
            self.add_type_var(node)
            for subtree in node.subtrees:
                self.__visit_type_var(subtree)
        elif node.root == '@':
            self.add_type_var(node)
            for subtree in node.subtrees:
                self.__visit_type_var(subtree)
        elif node.root == ':':
            self.add_type_var(node)
        elif node.root == 'id':
            self.add_type_var(node)
        elif node.root == 'let_':
            self.__visit_type_var(node.subtrees[1])
            self.__visit_type_var(node.subtrees[3])
            self.__visit_type_var(node.subtrees[5])

    def __call__(self, node: Tree) -> tuple[dict[int, str], dict[str: Tree]]:
        self.constraints = {}
        self.type_vars = {}
        self.bounded_vars = {}
        self.index = 0
        self.__visit_type_var(node)
        self.__visit_constraints(node)

        return self.type_vars, self.constraints
