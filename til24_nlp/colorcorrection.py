import spacy


__all__ = ["extract_adj_noun_pairs",
           "correct_pairs",
           "reconstruct_sentence",
           "process_text",
           ]

nlp = spacy.load('en_core_web_sm')
color_words = set(["black", "white", "red", "blue", "green", "yellow", "brown", "purple", "pink", "orange", "grey", "gray"])

# Function to extract adjective-noun pairs
def extract_adj_noun_pairs(doc):
    pairs = []
    for token in doc:
        if token.pos_ == 'ADJ' and token.head.pos_ == 'NOUN':
            pairs.append((token.text, token.head.text, token.i, token.head.i))
    return pairs

# Function to correct misinterpretations with specific rules
def correct_pairs(pairs, color_words):
    corrected_pairs = []
    for i, pair in enumerate(pairs):
        adjective, noun, adj_index, noun_index = pair

        # Check for adjacent colors rule
        if adjective in color_words:
            if i > 0:
                prev_adjective, prev_noun, prev_adj_index, prev_noun_index = pairs[i - 1]
                if prev_adjective in color_words:
                    if adjective == "white":
                        adjective = "light"
        
        corrected_pairs.append((adjective, noun, adj_index, noun_index))
    return corrected_pairs

# Function to replace original pairs with corrected pairs in the text
def reconstruct_sentence(text, doc, corrected_pairs):
    token_list = [token.text for token in doc]
    for adjective, noun, adj_index, noun_index in corrected_pairs:
        token_list[adj_index] = adjective
        token_list[noun_index] = noun
    
    corrected_text = []
    for token in token_list:
        if token in [",", ".", "!", "?", ":", ";"]:
            corrected_text[-1] += token  # Append punctuation to the previous token
        else:
            corrected_text.append(token)
    
    return ' '.join(corrected_text)


# Function to process the text
def process_text(text):
    doc = nlp(text)

    pairs = extract_adj_noun_pairs(doc)
    corrected_pairs = correct_pairs(pairs, color_words)
    corrected_text = reconstruct_sentence(text, doc, corrected_pairs)

    return corrected_text


