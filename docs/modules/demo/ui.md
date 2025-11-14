# Module: `demo/ui.py`

## Description

HypatiaX UI Components - Reusable UI building blocks
Provides rich console output, visualizations, and interactive components

**Last Modified**: 2025-11-10T20:41:45.013648

## Dependencies

- `dataclasses`
- `engine`
- `json`
- `pathlib`
- `typing`

## Constants

- `RESET`
- `BOLD`
- `DIM`
- `BLACK`
- `RED`
- `GREEN`
- `YELLOW`
- `BLUE`
- `MAGENTA`
- `CYAN`
- `WHITE`
- `BG_BLACK`
- `BG_RED`
- `BG_GREEN`
- `BG_YELLOW`
- `BG_BLUE`
- `BG_MAGENTA`
- `BG_CYAN`
- `BG_WHITE`
- `BRIGHT_BLACK`
- `BRIGHT_RED`
- `BRIGHT_GREEN`
- `BRIGHT_YELLOW`
- `BRIGHT_BLUE`
- `BRIGHT_MAGENTA`
- `BRIGHT_CYAN`
- `BRIGHT_WHITE`

## Classes

### `Colors`

ANSI color codes for terminal output

### `UIComponents`

Collection of reusable UI components

**Methods**:

- `header(text: str, width: int, char: str) -> str`
  - Create a formatted header
- `subheader(text: str, width: int, char: str) -> str`
  - Create a formatted subheader
- `box(text: str, width: int, padding: int, border_char: str) -> str`
  - Create a text box
- `table(headers: List[str], rows: List[List[Any]], col_widths: Optional[List[int]]) -> str`
  - Create a formatted table
- `progress_bar(current: int, total: int, width: int, prefix: str, suffix: str) -> str`
  - Create a progress bar
- `entity_visualization(text: str, entities: List[Dict[<ast.Tuple object at 0x7fa6f8633c10>]], use_colors: bool) -> str`
  - Visualize entities in text with colors/highlighting
- `formula_display(formula: str, confidence: float, use_colors: bool) -> str`
  - Display formula with confidence indicator
- `metric_cards(metrics: Dict[<ast.Tuple object at 0x7fa6f867dcd0>], columns: int) -> str`
  - Display metrics in card format
- `comparison_table(results: List[Dict[<ast.Tuple object at 0x7fa6f88817d0>]], show_entities: bool) -> str`
  - Create comparison table for multiple methods
- `menu(title: str, options: List[str], show_numbers: bool) -> str`
  - Create an interactive menu
- `status_message(message: str, status: str, use_icons: bool) -> str`
  - Display a status message
- `divider(width: int, char: str) -> str`
  - Create a horizontal divider

### `InteractiveDemo`

Interactive demo runner with rich UI

**Methods**:

- `__init__(self, engine)`
  - Initialize interactive demo
- `run(self)`
  - Run interactive demo loop
- `_process_query(self)`
  - Process a single query
- `_compare_methods(self)`
  - Compare multiple mapping methods
- `_view_history(self)`
  - View processing history
- `_show_statistics(self)`
  - Show engine statistics
