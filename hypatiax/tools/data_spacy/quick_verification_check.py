import spacy

nlp = spacy.load('hypatiax/data_spacy/queries/tableau/ner_tableau')
ruler = nlp.get_pipe('ruler_tableau')
print(f'Total patterns: {len(ruler.patterns)}')
print(f'First pattern: {ruler.patterns[0] if ruler.patterns else \"None\"}')
doc = nlp('Create a calculated field using SUM([Sales])')
print(f'Entities found: {[(e.text, e.label_) for e in doc.ents]}')
