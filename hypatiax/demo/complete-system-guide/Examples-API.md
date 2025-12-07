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
