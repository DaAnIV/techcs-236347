from lib.adt.tree.build import TreeAssistant
from lib.adt.tree import Tree, Walk

class RebuilderVisitor(Walk.Visitor):
    def __init__(self) -> None:
        self.type_vars = None
        self.type_results = None
        self.bounded_vars = None

    def type_result(self, node: Tree) -> Tree:
        return Tree.reconstruct(self.type_results[self.type_vars[id(node)]])

    def __visit(self, node: Tree, new_node: Tree):
        if node.root == '\\':
            self.__visit(node.subtrees[0], new_node.subtrees[0])
            self.bounded_vars[node.subtrees[0].terminals[0]] = True
            self.__visit(node.subtrees[1], new_node.subtrees[1])
            self.bounded_vars.pop(node.subtrees[0].terminals[0])
        elif node.root == '@':
            self.__visit(node.subtrees[0], new_node.subtrees[0])
            self.__visit(node.subtrees[1], new_node.subtrees[1])
        elif node.root == 'id':
            if node.subtrees[0].root not in self.bounded_vars:
                new_node.subtrees.clear()
                new_node.subtrees.append(Tree.reconstruct(node))
                new_node.subtrees.append(self.type_result(node))
                new_node.root = ':'
        elif node.root == 'let_':
            self.__visit(node.subtrees[1], new_node.subtrees[1])
            self.__visit(node.subtrees[3], new_node.subtrees[3])
            self.bounded_vars[node.subtrees[1].terminals[0]] = True
            self.__visit(node.subtrees[5], new_node.subtrees[5])
            self.bounded_vars.pop(node.subtrees[1].terminals[0])

    def __call__(self, node: Tree, type_vars: dict[int, str], type_results: dict[str, Tree]) -> Tree:
        new_tree = Tree.reconstruct(node)
        self.type_vars = type_vars
        self.type_results = type_results
        self.bounded_vars = {}
        self.__visit(node, new_tree)

        return new_tree
