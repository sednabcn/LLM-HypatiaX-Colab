Key Fixes Applied:

1. Deprecated API Usage (Critical)
Original Issues:

spacy.gold.biluo_tags_from_offsets() - Removed in spaCy v3
spacy.gold.spans_from_biluo_tags() - Removed in spaCy v3
spacy.tokens.Doc() manual construction - Problematic approach

Fixed:

offsets_to_biluo_tags() - Modern spaCy v3 function
biluo_tags_to_spans() - Modern spaCy v3 function
nlp.make_doc() - Proper way to create reference documents

2. Scorer Usage Issues
Original:

Created scorer without examples list
Used scorer.score(example) incorrectly (wrong method signature)
Accessed scorer.scores before proper evaluation

Fixed:

Collect all examples first
Use nlp.evaluate(examples) for batch evaluation
Alternative implementation with Scorer object for granular control

3. Missing Imports
Added:

Example from spacy.training
offsets_to_biluo_tags and biluo_tags_to_spans from spacy.training
Doc from spacy.tokens

4. Error Handling
Added:

Try-except blocks around example creation
Validation for empty examples list
Better error messages

5. Enhanced Features
Added:

Per-entity-type scoring breakdown
Better formatted output with separators
Alternative implementation using Scorer directly
Helper function to load data from DocBin files
Proper example usage in __main__ block

6. Bug Fixes
Fixed:

Changed t.ent_iob to t.ent_iob_ (correct attribute name)
Proper tuple unpacking in loop
Consistent dictionary key access with .get()

7. Documentation

Added comprehensive docstrings
Added usage examples
Explained parameters and return values

The code now works with spaCy v3+ and follows current best practices for NER model evaluation!RetryU2What does offsets_to_biluo_tags,?What does offsets_to_biluo_tags do?
offsets_to_biluo_tags converts entity span offsets (start, end positions) into BILUO tags for each token in a document.
BILUO Tagging Scheme
BILUO is a token-level tagging scheme where each token gets one of these tags:

B - Beginning (first token of a multi-token entity)
I - Inside (continuation of a multi-token entity)
L - Last (final token of a multi-token entity)
U - Unit (single-token entity)
O - Outside (not part of any entity)

Example
Let's say you have:
pythontext = "Apple Inc. was founded by Steve Jobs"
entities = [(0, 10, "ORG"), (26, 36, "PERSON")]
The function converts this to token-level tags:
TokenCharacter OffsetsBILUO TagApple0-5B-ORGInc.6-10L-ORGwas11-14Ofounded15-22Oby23-25OSteve26-31B-PERSONJobs32-36L-PERSON
Code Example
pythonimport spacy
from spacy.training import offsets_to_biluo_tags

nlp = spacy.blank("en")
text = "Apple Inc. was founded by Steve Jobs"
doc = nlp.make_doc(text)

entities = [(0, 10, "ORG"), (26, 36, "PERSON")]

biluo_tags = offsets_to_biluo_tags(doc, entities)
print(biluo_tags)

# Output: ['B-ORG', 'L-ORG', 'O', 'O', 'O', 'B-PERSON', 'L-PERSON']

# Display with tokens

for token, tag in zip(doc, biluo_tags):
    print(f"{token.text:10} -> {tag}")
Why This Matters
Character offsets → Token tags is necessary because:

Annotations are typically stored as character positions (easier for humans)
spaCy's NER works at the token level (more efficient for ML)
BILUO tags provide context about entity boundaries and multi-token entities

The Reverse Process
After prediction, you can convert back:
pythonfrom spacy.training import biluo_tags_to_spans

# Convert BILUO tags back to entity spans

spans = biluo_tags_to_spans(doc, biluo_tags)
doc.ents = spans  # Set entities on the document
This is exactly what happens in the fixed testing code - it converts your offset annotations to BILUO format so spaCy can properly compare predicted vs. reference entities at the token level!
