# /usr/bin/python3


class TreeNode:
    def __init__(self, name):
        self.name = name
        self.metrics = {}
        self.children = []

    def add_metric(self, key, value):
        if key in self.metrics:
            self.metrics[key] += value
        else:
            self.metrics[key] = value

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"{self.name}: {self.metrics}"


class TreeDict(TreeNode):
    def __init__(self, dictionary, name=None):
        super().__init__(name)
        self.dictionary = dictionary

    def is_tree(self, value):
        return isinstance(value, dict)

    def check_for_trees(self):
        """Recursively check and print if a dictionary
        contains tree-like nested dictionaries."""
        for key, value in self.dictionary.items():
            if self.is_tree(value):
                print(f"{key} is a tree : {value}")
                # Recursive call to explore deeper if needed
                check_for_trees(value)
            else:
                print(f"{key} is not a tree: {value}")

    def identify_root_and_subtrees(self, depth=0):
        """Recursive function to print root and subtrees
        with indentation based on depth."""
        if depth == 0:
            print("Root of the Tree:")
        else:
            print("\t" * depth + "Subtree at depth", depth, ":")

        for key, value in self.dictionary.items():
            if isinstance(value, dict):
                # Print current key and value to
                # indicate it's a nested dictionary (subtree)
                print("\t" * depth + f"{key}:")
                self.identify_root_and_subtrees(value, depth + 1)
            else:
                # Print current key and value to show
                # it's a leaf or non-dictionary value
                print("\t" * depth + f"{key}: {value}")

    def check_for_single_root(self):
        overarching_root = TreeNode("Overall Root")
        # Create one root to hold all sub-trees
        leaves = []
        roots = []

        for key, data in self.dictionary.items():
            if self.is_tree(data):
                # Create a new root node for this specific tree structure
                current_root = TreeNode(key)
                roots.append(key)
                # Populate the current root with children based on its tree structure
                for ent_type, metrics in data.items():
                    child = TreeNode(ent_type)
                    for metric, value in metrics.items():
                        child.add_metric(metric, value)
                    current_root.add_child(child)
                # Add this current root as a child of the overarching root
                overarching_root.add_child(current_root)
            else:
                # Handle leaf nodes
                leaves.append(key)

        return overarching_root, roots, leaves

    def check_for_root(self):
        leaves = []
        roots = []
        for key, data in self.dictionary.items():
            if self.is_tree(data):
                root = TreeNode(key)
                roots.append(key)
                # print("Root for key:", key)
                for ent_type, metrics in data.items():
                    child = TreeNode(ent_type)
                    for metric, value in metrics.items():
                        child.add_metric(metric, value)
                    root.add_child(child)
            else:
                leaves.append(key)
                # print("No root for key:", key)
        return root, roots, leaves

    def add_metrics(self, node1, node2):
        # Assume both nodes have the same structure
        new_node = TreeNode(node1.name)
        for key in node1.metrics:
            new_node.metrics[key] = node1.metrics[key] + node2.metrics[key]
        return new_node

    def avg_metrics(self, node, ntotal):
        new_node = TreeNode(node.name)
        for key in node.metrics:
            new_node.metrics[key] /= ntotal


class TreeOPDict(TreeDict):
    def __init__(self, dictionary=None, name=None):
        super().__init__(dictionary, name)

    def merge_trees(self, total_root, batch_root):
        for child in batch_root.children:
            existing_child = self.find_child_by_name(total_root, child.name)
            if existing_child:
                for key, value in child.metrics.items():
                    existing_child.add_metric(key, value)
            else:
                total_root.add_child(child)

    def find_child_by_name(self, node, name):
        for child in node.children:
            if child.name == name:
                return child
        return None

    def average_tree_metrics(self, node, num_batches):
        for key in node.metrics:
            node.metrics[key] /= num_batches

        for child in node.children:
            self.average_tree_metrics(child, num_batches)


"""
# Tests
# Example dictionary with nested structures
example_dict = {
    'key1': 'value1',
    'key2': {'sub_key1': 'sub_value1', 'sub_key2': {'sub_sub_key1': 'sub_sub_value1'}},
    'key3': 3.14,
    'key4': {'sub_key3': 'sub_value3'}
}

check_for_trees(example_dict)
root=[]
for key,_ in example_dict.items():
    root.append(key)
print(root)
# Example dictionary with nested structures
example_dict = {
    'key1': 'value1',
    'key2': {
        'sub_key1': 'sub_value1',
        'sub_key2': {
            'sub_sub_key1': 'sub_sub_value1'
        }
    },
    'key3': 3.14,
    'key4': {
        'sub_key3': 'sub_value3'
    }
}

identify_root_and_subtrees(example_dict)

example_dict={'token_acc': 1.0, 'token_p': 1.0, 'token_r': 1.0, 'token_f': 1.0, 'tag_acc': None, 'sents_p': None, 'sents_r': None, 'sents_f': None, 'dep_uas': None, 'dep_las': None, 'dep_las_per_type': None, 'pos_acc': None, 'morph_acc': None, 'morph_micro_p': None, 'morph_micro_r': None, 'morph_micro_f': None, 'morph_per_feat': None, 'lemma_acc': None, 'ents_p': 0.7837837837837838, 'ents_r': 0.7837837837837838, 'ents_f': 0.7837837837837838, 'ents_per_type': {'ADJ': {'p': 1.0, 'r': 1.0, 'f': 1.0}, 'ARGN': {'p': 0.0, 'r': 0.0, 'f': 0.0}, 'ADP': {'p': 1.0, 'r': 1.0, 'f': 1.0}, 'PRON': {'p': 1.0, 'r': 1.0, 'f': 1.0}, 'NOUN': {'p': 1.0, 'r': 0.9090909090909091, 'f': 0.9523809523809523}, 'PROPN': {'p': 1.0, 'r': 0.125, 'f': 0.2222222222222222}, 'VERB': {'p': 1.0, 'r': 1.0, 'f': 1.0}}, 'speed': 0.13276840323469435}

root,roots,leaves=TreeDict(example_dict).check_for_root()
print("roots:",roots)
print("leaves:", leaves)
print("root:",root)

print(root.children)

for child in root.children:
    print(child)

# Example usage:
# Adding metrics of ADJ and ADP
new_adj = TreeDict(example_dict).add_metrics(root.children[0], root.children[2])
print(new_adj)

print(root.children[0])
print(root.children[2])
print(len(root.children))
print(root.children)



"""
