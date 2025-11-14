📚 Full API Reference
Engine API

HypatiaXEngine.process(query, method, use_model) → ProcessingResult
HypatiaXEngine.batch_process(queries, method, use_model) → List[ProcessingResult]
HypatiaXEngine.extract_entities(text, use_model) → List[Entity]
HypatiaXEngine.generate_formula(query, entities, method) → str
HypatiaXEngine.export_results(results, output_path, format) → bool
HypatiaXEngine.get_stats() → Dict[str, Any]

UI API

UIComponents.header(text, width, char) → str
UIComponents.table(headers, rows, col_widths) → str
UIComponents.entity_visualization(text, entities, use_colors) → str
UIComponents.formula_display(formula, confidence, use_colors) → str
UIComponents.comparison_table(results, show_entities) → str
InteractiveDemo.run() → void

Examples API

ExampleManager.add_example(example) → bool
ExampleManager.filter_by_category(category) → List[Example]
ExampleManager.filter_by_difficulty(min, max) → List[Example]
ExampleManager.filter_by_tags(tags, match_all) → List[Example]
ExampleManager.get_random_examples(count, category, difficulty) → List[Example]
ExampleManager.split_dataset(train_ratio, val_ratio, test_ratio) → Tuple
ExampleManager.generate_variations(example, count) → List[Example]
ExampleManager.save_to_file(filepath, format) → void
ExampleManager.export_for_training(output_dir, split) → void