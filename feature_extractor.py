from gensim.models import Word2Vec, FastText
import gensim
import nltk
from transformers import BertTokenizer, BertModel
import torch
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import gensim.downloader

WINDOW_SIZE = 5  # Context window size
THREADS = 4  # Number of threads to use for training
CUTOFF_FREQ = 1  # Minimum frequency for a word to be included in vocabulary
EPOCHS = 10  # Number of training epochs

def list_of_lists(sentences):
    """
    Converts a list of sentences into a list of tokenized sentences.
    Each sentence is split into individual words.

    Args:
        sentences: List of strings where each string is a sentence.

    Returns:
        List of lists where each inner list contains tokens of a sentence.
    """
    tokenized_sentences = []
    for sentence in sentences:
        tokenized_sentences.append(nltk.word_tokenize(sentence))
    return tokenized_sentences


def train_gensim_w2v_model(tokenized_sentences, embedding_size):
    """
    Trains a Word2Vec model on the given corpus of sentences.

    Args:
        corpus: List of sentences (strings).

    Returns:
        A trained Gensim Word2Vec model.
    """
    model = Word2Vec(
        sentences=tokenized_sentences,
        vector_size=embedding_size,
        window=WINDOW_SIZE,
        min_count=CUTOFF_FREQ,
        workers=THREADS,
    )
    model.build_vocab(tokenized_sentences)
    model.train(
        corpus_iterable=tokenized_sentences,
        total_examples=model.corpus_count,
        epochs=EPOCHS,
    )
    return model


def train_gensim_fastext_model(tokenized_sentences, embedding_size):
    """
    Trains a Gensim FastText model on the given corpus of sentences.

    Args:
        corpus: List of sentences (strings).

    Returns:
        A trained Gensim FastText model.
    """
    model = FastText(
        sentences=tokenized_sentences,
        vector_size=embedding_size,
        window=WINDOW_SIZE,
        min_count=CUTOFF_FREQ,
        # workers=THREADS,
        epochs= EPOCHS
    )
    return model


def train_one_hot_encoding_model(tokenized_sentences):
    vocab = np.flatten(tokenized_sentences)
    enc = OneHotEncoder(handle_unknown="ignore")
    enc.fit(vocab)
    return enc


def get_one_hot_encoding(model, word):
    return model.transform([[word]])


def load_pretrained_model(model_name):
    """
    Loads a pretrained Word2Vec model from Gensim's library.

    Args:
        model_name: Name of the pretrained model to load.

    Returns:
        The loaded Gensim Word2Vec model.
    """
    model = gensim.downloader.load(model_name)
    return model


def embed_gensim(model, word):
    """
    Retrieves the word embedding for a given word using a trained Gensim model.
    Works for both w2v and fastext.

    Args:
        model: Trained Gensim Word2Vec model.
        word: Word to retrieve the embedding for.

    Returns:
        Word embedding as a vector.
    """
    return model.wv[word]


def init_bert():
    """
    Initializes a BERT model and its tokenizer.

    Args:
        None.

    Returns:
        A tuple containing the BERT model and its tokenizer.
    """
    model = BertModel.from_pretrained(
        "bert-base-uncased",
        output_hidden_states=True,
    )
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    return model, tokenizer


# def bert_text_preparation(text, tokenizer):
#     """
#     Prepares text for processing by the BERT model.

#     Args:
#         text: Input text as a string.
#         tokenizer: BERT tokenizer.

#     Returns:
#         Tuple containing:
#             - Tokenized text as a list of tokens.
#             - Tokens tensor for input to the BERT model.
#             - Segment tensors for input to the BERT model.
#     """
#     marked_text = "[CLS] " + text + " [SEP]"
#     tokenized_text = tokenizer.tokenize(marked_text)
#     indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
#     segments_ids = [1] * len(indexed_tokens)
#     tokens_tensor = torch.tensor([indexed_tokens])
#     segments_tensors = torch.tensor([segments_ids])
#     return tokenized_text, tokens_tensor, segments_tensors

# def bert_word_preparation(text, tokenizer):
#     """
#     Prepares text for processing by the BERT model.

#     Args:
#         text: Input text as a string.
#         tokenizer: BERT tokenizer.

#     Returns:
#         Tuple containing:
#             - Tokenized text as a list of tokens.
#             - Tokens tensor for input to the BERT model.
#             - Segment tensors for input to the BERT model.
#     """
#     marked_text = text
#     tokenized_text = tokenizer.tokenize(marked_text)
#     return tokenized_text

# def get_bert_embeddings(tokens_tensor, segments_tensors, model):
#     """
#     Retrieves token embeddings from a BERT model.

#     Args:
#         tokens_tensor: Tensor containing token indices.
#         segments_tensors: Tensor containing segment IDs.
#         model: BERT model.

#     Returns:
#         List of token embeddings as vectors.
#     """
#     with torch.no_grad():
#         outputs = model(tokens_tensor, segments_tensors)
#         hidden_states = outputs.hidden_states
#     token_embeddings = hidden_states[-1]
#     token_embeddings = torch.squeeze(token_embeddings, dim=0)
#     list_token_embeddings = [token_embed.tolist() for token_embed in token_embeddings]
#     return list_token_embeddings


# def get_word_bert_embedding(word, text, tokenizer, model):
#     """
#     Retrieves the embedding for a specific word in a given text using BERT.

#     Args:
#         word: Target word as a string.
#         text: Text containing the target word.
#         tokenizer: BERT tokenizer.
#         model: BERT model.

#     Returns:
#         Embedding vector for the target word.
#     """
#     tokenized_text, tokens_tensor, segments_tensors = bert_text_preparation(text, tokenizer)
#     tokenized_word = tokenizer.tokenize(word)  # Tokenize the target word
#     list_text_embeddings = get_bert_embeddings(tokens_tensor, segments_tensors, model)
#     tok_indexes = [i for i, tok in enumerate(tokenized_text) if tok in tokenized_word]

#     # if not tok_indexes:
#     #     raise ValueError(f"Word '{word}' not found in tokenized text.")

#     tok_embeddings = [list_text_embeddings[i] for i in tok_indexes]
#     average_embedding = np.mean(tok_embeddings, axis=0)
#     return average_embedding

def get_embedding_bert(word, text, model, tokenizer):
    """
    Retrieves the embedding for a given word in text using BERT.

    Args:
        word: Word to retrieve the embedding for.
        text: Text containing the word.
        model: BERT model.
        tokenizer: BERT tokenizer.

    Returns:
        Embedding vector for the word.
    """
    encoding = tokenizer.batch_encode_plus( [text],
        padding=True,
        truncation=True,
        return_tensors='pt',
        add_special_tokens=True
    )
    input_ids = encoding['input_ids']
    attention_mask = encoding['attention_mask']
    tokenized_text = tokenizer.convert_ids_to_tokens(input_ids[0]) 

    tokenized_word = tokenizer.tokenize(word)
    word_indices = [
        i for i, token in enumerate(tokenized_text)
        if token in tokenized_word
    ]
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        word_embeddings = outputs.last_hidden_state
    word_token_embeddings = word_embeddings[0][word_indices]

    word_embedding = torch.mean(word_token_embeddings, dim=0)
    return word_embedding.numpy()

# model, tokenizer = init_bert()
# print(get_embedding_bert("Hello","Hello, world!", model, tokenizer))
