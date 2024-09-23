import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import random
import re
from py_thesaurus import Thesaurus

# Download NLTK resources
@st.cache_resource
def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')

download_nltk_resources()

# Get English stopwords
stop_words = set(stopwords.words('english'))

def get_synonyms(word, pos='noun'):
    thesaurus = Thesaurus(word)
    try:
        synonyms = thesaurus.get_synonym(pos=pos)
        return [syn for syn in synonyms if syn.isalpha() and len(syn.split()) == 1 and len(syn) <= 10]
    except:
        return []

def introduce_human_errors(text):
    words = text.split()
    for i in range(len(words)):
        if random.random() < 0.05:  # 5% chance of introducing an error
            error_type = random.choice(['double_space', 'typo'])
            if error_type == 'double_space':
                words[i] = "  " + words[i]  # Introduce a double space
            elif error_type == 'typo' and len(words[i]) > 3:
                pos = random.randint(1, len(words[i]) - 2)
                words[i] = words[i][:pos] + words[i][pos] + words[i][pos:]  # Duplicate a letter
    return ' '.join(words)

def paraphrase_sentence(sentence):
    quote_pattern = r'(".*?")'
    parts = re.split(quote_pattern, sentence)
    
    new_parts = []
    for part in parts:
        if part.startswith('"') and part.endswith('"'):
            new_parts.append(part)  # Keep quoted text as is
        else:
            words = word_tokenize(part)
            pos_tags = nltk.pos_tag(words)
            new_words = []

            num_words_to_replace = int(len(words) * 0.3)  # Replace approximately 30% of words
            words_replaced = 0

            for word, tag in pos_tags:
                if words_replaced >= num_words_to_replace:
                    new_words.append(word)
                elif tag.startswith('NN') or tag.startswith('VB') or tag.startswith('JJ') or tag.startswith('RB'):
                    if word.lower() not in stop_words:
                        pos = 'noun' if tag.startswith('NN') else 'verb' if tag.startswith('VB') else 'adj'
                        synonyms = get_synonyms(word, pos)
                        if synonyms:
                            synonym = random.choice(synonyms)
                            new_words.append(synonym)
                            words_replaced += 1
                        else:
                            new_words.append(word)
                    else:
                        new_words.append(word)
                else:
                    new_words.append(word)

            new_parts.append(' '.join(new_words))

    return ''.join(new_parts)

def paraphrase_text(input_text):
    paragraphs = input_text.split('\n\n')
    paraphrased_paragraphs = []

    for paragraph in paragraphs:
        sentences = sent_tokenize(paragraph)
        paraphrased_sentences = [paraphrase_sentence(sentence) for sentence in sentences]
        paraphrased_paragraph = ' '.join(paraphrased_sentences)
        paraphrased_paragraph = introduce_human_errors(paraphrased_paragraph)
        paraphrased_paragraphs.append(paraphrased_paragraph)

    return '\n\n'.join(paraphrased_paragraphs)

def main():
    st.title("Humanizer")

    input_text = st.text_area("Enter text to humanize:", height=200)

    if st.button("Paraphrase"):
        if input_text:
            with st.spinner("Paraphrasing..."):
                paraphrased_text = paraphrase_text(input_text)
            st.subheader("Humanized Text:")
            st.text_area("", value=paraphrased_text, height=200, key="output")
            st.button("Copy to Clipboard", on_click=lambda: st.write("Text copied to clipboard!"))
        else:
            st.warning("Please enter text to paraphrase.")

if __name__ == "__main__":
    main()
