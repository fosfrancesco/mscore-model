from fractions import Fraction
import lib.score_comparison_lib as scl
from lib.NoteTree_v2 import NoteNode
from graphviz import Digraph

class Node:
    def __init__(self, parent, type):
        """
        The generic Tree node class
        :param parent: a Node instance
        :param type: a string that can be "operation" or "group" or "sub" or "skip"
        """
        self.type = type
        self.children = [] #each child is a Node
        self.parent = parent
        self.subtree_cost = None #we initialize that when the subtree is builded and complete
        self.subtree_hash = None #we initialize that when the subtree is builded and complete
        if self.type != "root":
            parent.add_child(self) #add a child in the parent Node if the parent is not the root

    def get_subtree_cost(self):
        return self.subtree_cost

    def get_type(self):
        return self.type

    def get_parent(self):
        return self.parent

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        """
        :return: an array of Node
        """
        return self.children

    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()

    def to_string(self):
        """
        Return the string representation of the subtree under the Node
        This class is override in InternalNode and LeafNode to make the recursion stop
        """
        out_string= "("
        for c in self.get_children():
            out_string= out_string + c.to_string() + ","
        out_string = out_string[0:-1] #remove the last comma
        out_string += ")" #close the grouping
        return out_string
    
    def __eq__(self, other):
        return self.to_string() == other.to_string()


class Root(Node):
    def __init__(self):
        Node.__init__(self, None,"root")
        self.cost= None
        self.cost_computed = False

    def get_parent(self):
        raise TypeError('Root nodes have no parent')

    def compute_cost(self):
        #the cost for a sub is the minimum of his group children
        for n in self.get_children():
            assert(n.get_type()== "group") #only group are allowed as children
            assert(n.cost_computed) #check if the cost is already computed (should be)
        self.cost = min([n.cost for n in self.get_children()])
        self.cost_computed = True

class GroupNode(Node):
    def __init__(self, parent ):
        Node.__init__(self, parent, "group")
        self.operation="group"
        self.cost_computed = False
        self.cost = None

    def compute_cost(self): #the cost is the the sum of the operation costs
        cost = 0
        for n in self.get_children():
            if n.get_type() == "operation":
                if n.operation[0] == "ins":
                    cost += n.operation[2].subtree_size()
                elif n.operation[0] == "del":
                    cost += n.operation[1].subtree_size()
            elif n.get_type() == "sub" :
                assert(n.cost_computed)
                cost += n.cost
            elif n.get_type() == "skip" :
                assert(n.cost_computed)
                cost += n.cost
            else: #group cannot have other group as children
                raise ValueError("Invalide node type: " + str(n.get_type()))
        self.cost = cost
        self.cost_computed = True
    
    def to_string(self):
        """
            Return the string representation of the subtree under the Node
            """
        out_string= "group"
        return out_string + super(GroupNode, self).to_string()


class OperationNode(Node):
    def __init__(self, parent, operation ):
        """
        Class for ins, del and nop operations.
        :param parent is a Node
        :param operation is a triple in the format ("ins/del/nop",elem1,elem2)
        """
        assert(operation[0]=="ins" or operation[0]=="del" or operation[0]=="nop") 
        Node.__init__(self, parent, "operation")
        self.operation = operation

    def get_operation(self):
        return self.operation

    def to_string(self):
        return str(self.operation)


class SubNode(Node):
    def __init__(self, parent, operation):
        Node.__init__(self, parent, "sub")
        self.operation = operation
        self.cost_computed = False
        self.cost = None

    def get_operation(self):
        return self.operation

    def to_string(self):
        """
        Returns:
            str -- the str representation of the operation
        """
        out_string= str(self.operation)
        return out_string + super(SubNode, self).to_string()

    def compute_cost(self):
        if len(self.get_children())==0: #sub is a leaf
            if type(self.operation[1]) is NoteNode and type(self.operation[2]) is NoteNode: #if it is a substitution between 2 NoteNodes
                self.cost = scl.evaluate_noteNode_diff(self.operation[1],self.operation[2])
                self.cost_computed = True
            else: #if it is a sub between InternalNode and NoteNode
                self.cost = abs(self.operation[1].subtree_size() - self.operation[2].subtree_size()) + 1
                self.cost_computed = True
        else:
            #the cost for a sub is the minimum of his group children
            for n in self.get_children():
                assert(n.get_type()== "group") #only group are allowed as children
                assert(n.cost_computed) #check if the cost is already computed (should be)
            self.cost = min([n.cost for n in self.get_children()])
            self.cost_computed = True

class SkipNode(Node):
    def __init__(self, parent, operation):
        Node.__init__(self, parent, "skip")
        self.operation = operation
        self.cost_computed = False
        self.cost = None

    def get_operation(self):
        return self.operation

    def to_string(self):
        """
        Returns:
            str -- the str representation of the operation
        """
        out_string= str(self.operation)
        return out_string + super(SkipNode, self).to_string()

    def compute_cost(self):
        if len(self.get_children())==0: #sub is a leaf
            self.cost = 1
            self.cost_computed = True
        else:
            #the cost for a sub is the cost of his children + 1
            childrens = self.get_children()
            assert(len(childrens)==1 )
            assert(childrens[0].get_type()== "group") #only group are allowed as children
            assert(childrens[0].cost_computed) #check if the cost is already computed (should be)
            self.cost = childrens[0].cost + 1
            self.cost_computed = True

class DiffTree:
    def __init__(self, tree1, tree2):
        """
        :param seq1: the original tree
        :param seq2: the compare_to tree
        """
        self.root = Root()
        self.multilevel_edit_distance_tree(tree1.get_children(), tree2.get_children(), self.root)
        self.root.compute_cost()

    def nested_edit_distance_tree(self,seq1, seq2, parent):
        #return a tree instead of a list of lists
        cost, path = scl.iterative_levenshtein(seq1, seq2, verbosity=4)
        for group in path: #for each possible group
            group_node = GroupNode(parent)
            for op in group : #for each operation in the group
                if op[0]== "ins" or op[0]=="del" or op[0]== "nop" : #if ins or del just append them
                    op_node = OperationNode(group_node,op)
                else: #if it is a sub
                    sub_node = SubNode(group_node,op)
                    if op[1].get_type()=="note" or op[2].get_type()=="note":  #end of recursion if we reach leaves for a specific sub
                        sub_node.compute_cost() #cost with no child = 1     
                    else: #recursion call for the sub
                        self.nested_edit_distance_tree(op[1].get_children(),op[2].get_children(), sub_node )
                        sub_node.compute_cost()
            group_node.compute_cost()

        #now delete the groupNode with a cost more than the minimum (among groupNodes)
        best_cost = min([elem.cost for elem in parent.get_children() if elem.get_type()=="group"])
        parent.children= [node for node in parent.children if  node.get_type() == "group" and  node.cost == best_cost]
        return

    def multilevel_edit_distance_tree(self,seq1, seq2, parent):
        #for seq with a single elements we can go down in the recursion
        if len(seq1) == 1 and seq1[0].get_type()!="note":
            group_node = GroupNode(parent)
            skip_node = SkipNode(group_node,"skip")
            self.multilevel_edit_distance_tree(seq1[0].get_children(),seq2, skip_node )
            skip_node.compute_cost()
            group_node.compute_cost()
        elif len(seq2) == 1 and seq2[0].get_type()!="note":
            group_node = GroupNode(parent)
            skip_node = SkipNode(group_node,"skip")
            self.multilevel_edit_distance_tree(seq1,seq2[0].get_children(), skip_node )
            skip_node.compute_cost()
            group_node.compute_cost()

        #for multiple elements or for single element sequence we compute the edit distance
        cost, path = scl.iterative_levenshtein(seq1, seq2, verbosity=4)
        for group in path: #for each possible group
            group_node = GroupNode(parent)
            for op in group : #for each operation in the group
                if op[0]== "ins" or op[0]=="del" or op[0]== "nop" : #if ins or del just append them
                    op_node = OperationNode(group_node,op)
                else: #if it is a sub
                    sub_node = SubNode(group_node,op)
                    if op[1].get_type()=="note" or op[2].get_type()=="note":  #end of recursion if we reach leaves for a specific sub
                        sub_node.compute_cost() #cost with no child = 1     
                    else: #recursion call for the sub
                        self.multilevel_edit_distance_tree(op[1].get_children(),op[2].get_children(), sub_node )
                        sub_node.compute_cost()
            group_node.compute_cost()

        #now delete the groupNode with a cost more than the minimum (among groupNodes)
        best_cost = min([elem.cost for elem in parent.get_children() if elem.get_type()=="group"])
        parent.children= [node for node in parent.children if  node.get_type() == "group" and  node.cost == best_cost]
        return

    def get_cost(self):
        return self.root.cost

    def get_root(self):
        return self.root

    def get_nodes(self, local_root = None):
        if local_root is None:
            local_root = self.root
        return self._all_nodes(local_root, [])

    def get_note_nodes(self, local_root = None):
        if local_root is None:
            local_root = self.root
        return [n for n in self.get_nodes(local_root = local_root) if n.get_type() == "note"]

    def _all_nodes(self, node, children_list):
        for c in node.get_children_node():
            self._all_nodes(c, children_list)
        children_list.append(node)  # add the current node
        return children_list
    
    def show(self, save=False, name = ""):
        """Print a graphical version of the tree"""
        tree_repr = Digraph(comment='Duration Tree')
        tree_repr.node("1", "root")  # the root
        self._recursive_tree_display(self.get_root(), tree_repr, "11")
        if save:
            tree_repr.render('test-output/' + 'diffTree' + name, view=True)
        return tree_repr

    def _recursive_tree_display(self, node, _tree, name):
        """The actual recursive function called by show() """
        for l in node.get_children():
            if len(l.get_children()) == 0:  # if it is a leaf
                _tree.node(name, l.to_string(), shape='box')
                _tree.edge(name[:-1], name ,constraint='true')
                name = name[:-1] + str(int(name[-1]) + 1)
            else:
                _tree.node(name, str(l.operation))
                # _tree.node(name, str(l.get_duration()))
                _tree.edge(name[:-1], name, constraint='true')
                self._recursive_tree_display(l, _tree, name + "1")
                name = name[:-1] + str(int(name[-1]) + 1)
    
    # def list_of_paths():
    #     paths = []
    #     for child in root.

    # def recursive_list_of_paths(node):
    #     paths= []
    #     if len(node.chilren) == 0: #it is a leaves: operation or sub node with no children
    #         paths.append(node.operation)
    #     elif node.type == "sub" or node.type == "skip" : #if is the parent of groups
    #         for child in node.children:
    #             assert(child.type == "group") #at the same level only groups
    #             granchildren_path=[]
    #             for grandchild in child.children:
    #                 granchildren_path.append(recursive_list_of_paths(grandchild))
    #             paths.append(granchildren_path)
    #             ##############################################
    #             #devo moltiplicare il numero di soluzioni per i figli di group ogni volta

    
    def to_string(self):
        """
        Returns the string unique representation of the tree
        """
        return self.root.to_string()

































