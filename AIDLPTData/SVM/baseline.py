import json
import numpy as np
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from scipy.special import kl_div
import pickle
from pathlib import Path

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def word_count(text):
    return len(nltk.word_tokenize(text))

def sentence_lengths(text):
    # straightforward, using nltk instead of .split() to handle punctuation and edge cases (according to ChatGPT)
    doc = nlp(text)
    res = [] 
    for sent in doc.sents:
        res.append(len(nltk.word_tokenize(sent.text)))
    return res

def compute_kl_divergence(tfidf_vector, vocab_size):
    # sparse TFIDF vector to a dense array
    tfidf_dense = tfidf_vector.toarray()[0]

    # total weight (sum of TFIDF values)
    total = tfidf_dense.sum()

    # normalize to get a probability dist when > 0 
    if total > 0:
        p = tfidf_dense / total
    else:
        # if 0, use normal dist 
        p = np.ones(vocab_size) / vocab_size

    # uniform dist to compare 
    q = np.ones(vocab_size) / vocab_size

    # KL divergence between p and q
    divergence = kl_div(p, q)

    # sum for final score 
    return divergence.sum()

def compute_train_statistics(train_docs):

    # word count per doc using pre-def function 
    doc_word_count = []
    for doc in train_docs: 
        doc_word_count.append(word_count(doc))

    # word count per sentence per doc  
    sentence_word_counts = []
    for doc in train_docs:
        sentence_word_counts.extend(sentence_lengths(doc))

    mean_doc_wc = np.mean(doc_word_count)
    std_doc_wc = np.std(doc_word_count)
    mean_sent_wc = np.mean(sentence_word_counts)
    std_sent_wc = np.std(sentence_word_counts)

    print("Doc word count mean/std:", mean_doc_wc, std_doc_wc)
    print("Sent word count mean/std:", mean_sent_wc, std_sent_wc)

    # this is going to be used for z-score calc later, if i'm understanding correct, there is no need to keep track 
    # of per document statistics of avg wc per sentence, just returning each sentence's word count across ALL docs
    return mean_doc_wc, std_doc_wc, mean_sent_wc, std_sent_wc

def build_tfidf(train_docs, dev_docs):
    # make a TFIDF vectorizer object from scikit-learn
    # 'learn' the vocabulary from the training documents and compute TFIDF scores
    tfidf = TfidfVectorizer()

    # fit the TFIDF model on the training documents and transform them into a sparse matrix
    # each document is now represented as a vector of TFIDF values based on the learned vocabulary (only ones in training set)
    tfidf_train = tfidf.fit_transform(train_docs)

    # transform the development documents using the same vocabulary and IDF values learned from training data
    # ensures consistency: dev documents are mapped using the same feature space
    tfidf_dev = tfidf.transform(dev_docs)

    # compute the vocabulary size, i.e., the number of unique words (features) learned from the training data
    vocab_size = len(tfidf.vocabulary_)

    return tfidf, tfidf_train, tfidf_dev, vocab_size

def build_pca_kmeans(tfidf_train):
    # convert the sparse TFIDF matrix to a dense NumPy array
    # necessary because PCA does not accept sparse input
    tfidf_dense = tfidf_train.toarray()

    # create a PCA (Principal Component Analysis) object to reduce dimensionality.
    # we set n_components=2 because we want to reduce the original TFIDF vectors (which may have thousands of dimensions)
    # into 2 dimensions, helps with visualizations and simplifies clustering
    pca = PCA(n_components=2)

    # fit the PCA model to the dense TFIDF vectors and transform them.
    # this line does two things:
    #   - learns the top 2 principal components (directions of highest variance in the data)
    #   - projects each TFIDF vector onto these 2 components
    # the result is a new matrix of shape (num_documents, 2)
    tfidf_pca = pca.fit_transform(tfidf_dense)

    # create a KMeans clustering model
    # we choose 200 clusters arbitrarily to represent different "types" or "themes" of documents in the data
    # the random_state ensures reproducibility (you get the same clusters every time you run it)
    kmeans = KMeans(n_clusters=200, random_state=42)

    # fit the KMeans model to the 2D PCA-reduced data and assign each document to a cluster
    # this returns a list of cluster indices — one for each document — indicating which group it belongs to
    cluster_indices = kmeans.fit_predict(tfidf_pca)

    # return the trained PCA and KMeans models so they can be reused later
    return pca, kmeans

def extract_features_for_docs(docs, tfidf_model, pca_model, kmeans_model, stats, vocab_size):
    mean_doc_wc, std_doc_wc, mean_sent_wc, std_sent_wc = stats
    features = []

    for doc in docs:
        # The first feature is just the number of words in the document, minus np.mean(L), all divided by np.std(L).
        wc = word_count(doc)
        f1 = (wc - mean_doc_wc) / std_doc_wc

        # To calculate the second feature, count the words in each sentence of the document. For each sentence, subtract np.mean(M) from the count and divide the difference by np.std(M). This is the z-score for the sentence. The final feature is the mean over all sentences of these z-scores.
        sents = sentence_lengths(doc)
        z_scores = []
        if sents:
            for s in sents:
                z = (s - mean_sent_wc) / std_sent_wc
                z_scores.append(z)
            f2 = np.mean(z_scores)
        else:
            f2 = 0.0

        # To calculate the third feature, you first count the number of times each vocabulary word appears in the sentence (the unigram distribution of the document). This should be a list of integers of length V, where V is the size of the vocabulary. Probably the TFIDF code will do this for you. The other distibution you need is just 1/V*np.ones(V). Then you just pass those two distributions
        # to scipy.special.kl_div() (or some other implementation).
        tfidf_vec = tfidf_model.transform([doc])
        f3 = compute_kl_divergence(tfidf_vec, vocab_size)

        # To calculate the fourth feature, first run the document through TFIDF model you saved. The run the output through the k-means model you saved. This will result in a single integer between 0 and 199.
        tfidf_reduced = pca_model.transform(tfidf_vec.toarray())
        f4 = kmeans_model.predict(tfidf_reduced)[0]

        features.append([f1, f2, f3, f4])

    return np.array(features)

def save_models(tfidf, pca, kmeans, stats):
    mean_doc_wc, std_doc_wc, mean_sent_wc, std_sent_wc = stats
    with open("models.pkl", "wb") as f:
        pickle.dump({
            'tfidf': tfidf,
            'pca': pca,
            'kmeans': kmeans,
            'mean_doc_wc': mean_doc_wc,
            'std_doc_wc': std_doc_wc,
            'mean_sent_wc': mean_sent_wc,
            'std_sent_wc': std_sent_wc,
        }, f)

# straightforward training
def train_svm(X_train, y_train):
    clf = SVC()
    clf.fit(X_train, y_train)
    with open("svm_model.pkl", "wb") as f:
        pickle.dump(clf, f)
    return clf

def evaluate_model(clf, X_dev, y_dev):
    # use the trained classifier to predict labels for the development set
    y_pred = clf.predict(X_dev)

    # calculate the accuracy by comparing predicted and actual labels
    acc = (y_pred == y_dev).mean()

    print(f"Dev Accuracy: {acc:.3f}")

def load_documents(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    documents = []
    labels = []

    for line in lines:
        obj = json.loads(line)

        # change these depending on what json object labels are 
        documents.append(obj['text']) 
        labels.append(obj['label'])  

    return documents, labels

def load_data():
    # all running through this one program for simplicity sake, so keep all files in one dir
    base_path = Path(".")
    train_path = base_path / "trainEnglish.json"
    dev_path = base_path / "devEnglish.json"
    train_docs, train_labels = load_documents(train_path)
    dev_docs, dev_labels = load_documents(dev_path)
    return train_docs, train_labels, dev_docs, dev_labels

def main():
    # load data and labels
    data = load_data()
    train_docs = data[0]
    train_labels = data[1]
    dev_docs = data[2]
    dev_labels = data[3]

    # compute statistics
    stats = compute_train_statistics(train_docs)

    # build TFIDF and vocabulary size
    tfidf_build = build_tfidf(train_docs, dev_docs)
    tfidf = tfidf_build[0]
    tfidf_train = tfidf_build[1]
    tfidf_dev = tfidf_build[2]
    vocab_size = tfidf_build[3]

    # build PCA and KMeans models
    pca_kmeans_result = build_pca_kmeans(tfidf_train)
    pca = pca_kmeans_result[0]
    kmeans = pca_kmeans_result[1]

    # save the models
    save_models(tfidf, pca, kmeans, stats)

    # encode the labels
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(train_labels)
    y_dev = label_encoder.transform(dev_labels)

    # extract features for train and dev documents
    X_train = extract_features_for_docs(train_docs, tfidf, pca, kmeans, stats, vocab_size)
    X_dev = extract_features_for_docs(dev_docs, tfidf, pca, kmeans, stats, vocab_size)

    # train the SVM and evaluate the model
    clf = train_svm(X_train, y_train)
    evaluate_model(clf, X_dev, y_dev)

if __name__ == "__main__":
    main()

