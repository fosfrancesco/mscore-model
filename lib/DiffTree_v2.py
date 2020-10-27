from fractions import Fraction
import lib.score_comparison_lib as scl
from lib.NoteTree_v2 import NoteNode
from graphviz import Digraph

class Node:
    def __init__(self, parent, type, cost, elem1, elem2):
        """
        The generic Tree node class
        :param parent: a Node instance
        :param type: a string that can be "root","nop", "sub", "ins", "del", "sub", "leftdesc", "rightdesc", "desc"
        """
        self.type = type
        self.children = [] #each child is a Node
        self.parent = parent
        self.subtree_cost = None #we initialize that when the subtree is builded and complete
        self.subtree_hash = None #we initialize that when the subtree is builded and complete
        if self.type != "root":
            parent.add_child(self) #add a child in the parent Node if the parent is not the root
        self.elem1 = elem1
        self.elem2 = elem2
        self.cost = cost

    def add_child(self, child):
        self.children.append(child)

    def has_children(self):
        if len(self.children) == 0:
            return False
        else:
            return True
    
    def __repr__(self):
        return self.to_string()

    def to_string(self):
        """
        Return the string representation of the subtree under the Node
        This class is override in InternalNode and LeafNode to make the recursion stop
        """
        out_string= "("
        for c in self.children:
            out_string= out_string + c.to_string() + ","
        out_string = out_string[0:-1] #remove the last comma
        out_string += ")" #close the grouping
        return out_string
    
    def __eq__(self, other):
        return self.to_string() == other.to_string()


class Root(Node):
    def __init__(self):
        Node.__init__(self, None,"root",0,None, None)
        self.cost= None

class OpNode(Node):
    def __init__(self,parent,operation,cost,elem1, elem2):
        Node.__init__(self, parent,operation,cost, elem1, elem2 )
        self.cost= cost
        self.operation = operation

    def to_string(self):
        if self.has_children():
            return self.operation + super(OpNode, self).to_string() #just the name of operation, without elems for clarity
        else: #if there are no child
            return "{}:{},{}".format(self.operation,self.elem1,self.elem2)

# class InsNode(Node):
#     def __init__(self,parent,cost,elem1, elem2):
#         Node.__init__(self, parent,"ins",cost, elem1, elem2 )
#         self.cost= cost 

# class DelNode(Node):
#     def __init__(self,parent,cost,elem1, elem2):
#         Node.__init__(self, parent,"del",cost, elem1, elem2 )
#         self.cost= cost 

# class NopNode(Node):
#     def __init__(self,parent,cost,elem1, elem2):
#         Node.__init__(self, parent,"nop",cost, elem1, elem2 )
#         self.cost= cost 

# class SubNode(Node):
#     def __init__(self,parent,cost,elem1, elem2):
#         Node.__init__(self, parent,"sub",cost, elem1, elem2 )
#         self.cost= cost 

# class LeftDescNode():


class DiffTree:
    def __init__(self, root):
        self.root = root

    def get_cost(self):
        return self.root.cost

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
        self._recursive_tree_display(self.root, tree_repr, "11")
        if save:
            tree_repr.render('test-output/' + 'diffTree' + name, view=True)
        return tree_repr

    def _recursive_tree_display(self, node, _tree, name):
        """The actual recursive function called by show() """
        for l in node.children:
            if len(l.children) == 0:  # if it is a leaf
                _tree.node(name, l.to_string(), shape='box')
                _tree.edge(name[:-1], name ,constraint='true')
                name = name[:-1] + str(int(name[-1]) + 1)
            else:
                _tree.node(name, "{}:{}{}".format(l.operation,l.elem1,l.elem2))
                # _tree.node(name, str(l.get_duration()))
                _tree.edge(name[:-1], name, constraint='true')
                self._recursive_tree_display(l, _tree, name + "1")
                name = name[:-1] + str(int(name[-1]) + 1)
    
   
    def to_string(self):
        """
        Returns the string unique representation of the tree
        """
        return self.root.to_string()

































