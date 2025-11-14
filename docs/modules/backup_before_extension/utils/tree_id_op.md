# Module: `backup_before_extension/utils/tree_id_op.py`

**Last Modified**: 2025-11-04T16:01:28.481769

## Classes

### `TreeNode`

**Methods**:

- `__init__(self, name)`
- `add_metric(self, key, value)`
- `add_child(self, child)`
- `__repr__(self)`

### `TreeDict`

**Inherits from**: `TreeNode`

**Methods**:

- `__init__(self, dictionary, name)`
- `is_tree(self, value)`
- `check_for_trees(self)`
  - Recursively check and print if a dictionary
- `identify_root_and_subtrees(self, depth)`
  - Recursive function to print root and subtrees
- `check_for_single_root(self)`
- `check_for_root(self)`
- `add_metrics(self, node1, node2)`
- `avg_metrics(self, node, ntotal)`

### `TreeOPDict`

**Inherits from**: `TreeDict`

**Methods**:

- `__init__(self, dictionary, name)`
- `merge_trees(self, total_root, batch_root)`
- `find_child_by_name(self, node, name)`
- `average_tree_metrics(self, node, num_batches)`
