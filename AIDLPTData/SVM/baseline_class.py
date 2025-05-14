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

class AutoILR:
    def __init__(self, trainingPath="trainEnglish.json", devPath="devEnglish.json",
                 desiredFeatures=[1, 2, 3, 4], numberPCAComponents=10, numberClusters=300):
        self.trainingPath = Path(trainingPath)
        self.devPath = Path(devPath)
        self.desiredFeatures = desiredFeatures
        self.numberPCAComponents = numberPCAComponents
        self.numberClusters = numberClusters

    def word_count(self, text):
        return len(nltk.word_tokenize(text))

    def sentence_lengths(self, text):
        # straightforward, using nltk instead of .split() to handle punctuation and edge cases
        doc = nlp(text)
        res = [len(nltk.word_tokenize(sent.text)) for sent in doc.sents]
        return res

    def compute_kl_divergence(self, tfidf_vector, vocab_size):
        tfidf_dense = tfidf_vector.toarray()[0]
        total = tfidf_dense.sum()
        if total > 0:
            p = tfidf_dense / total
        else:
            p = np.ones(vocab_size) / vocab_size
        q = np.ones(vocab_size) / vocab_size
        divergence = kl_div(p, q)
        return divergence.sum()

    def calculate_training_statistics(self, documents):
        doc_word_count = [self.word_count(doc) for doc in documents]
        sentence_word_counts = []
        for doc in documents:
            sentence_word_counts.extend(self.sentence_lengths(doc))

        self.mean_doc_wc = np.mean(doc_word_count)
        self.std_doc_wc = np.std(doc_word_count)
        self.mean_sent_wc = np.mean(sentence_word_counts)
        self.std_sent_wc = np.std(sentence_word_counts)

        print("Doc word count mean/std:", self.mean_doc_wc, self.std_doc_wc)
        print("Sent word count mean/std:", self.mean_sent_wc, self.std_sent_wc)

    def fit_tfidf(self, train_docs, dev_docs):
        self.tfidf = TfidfVectorizer()
        self.tfidf_train = self.tfidf.fit_transform(train_docs)
        self.tfidf_dev = self.tfidf.transform(dev_docs)
        self.vocab_size = len(self.tfidf.vocabulary_)

    def fit_pca_kmeans(self):
        tfidf_dense = self.tfidf_train.toarray()
        self.pca = PCA(n_components=self.numberPCAComponents)
        self.tfidf_pca = self.pca.fit_transform(tfidf_dense)
        self.kmeans = KMeans(n_clusters=self.numberClusters, random_state=42)
        self.cluster_indices = self.kmeans.fit_predict(self.tfidf_pca)

    def extract_features(self, documents):
        features = []
        for doc in documents:
            row = []
            if 1 in self.desiredFeatures:
                wc = self.word_count(doc)
                f1 = (wc - self.mean_doc_wc) / self.std_doc_wc
                row.append(f1)
            if 2 in self.desiredFeatures:
                sents = self.sentence_lengths(doc)
                z_scores = [(s - self.mean_sent_wc) / self.std_sent_wc for s in sents] if sents else [0.0]
                f2 = np.mean(z_scores)
                row.append(f2)
            if 3 in self.desiredFeatures:
                tfidf_vec = self.tfidf.transform([doc])
                f3 = self.compute_kl_divergence(tfidf_vec, self.vocab_size)
                row.append(f3)
            if 4 in self.desiredFeatures:
                tfidf_vec = self.tfidf.transform([doc])
                tfidf_reduced = self.pca.transform(tfidf_vec.toarray())
                f4 = self.kmeans.predict(tfidf_reduced)[0]
                row.append(f4)
            features.append(row)
        return np.array(features)

    def train_svm(self, X_train, y_train):
        self.svm = SVC()
        self.svm.fit(X_train, y_train)
        with open("svm_model.pkl", "wb") as f:
            pickle.dump(self.svm, f)

    def evaluate_model(self, X_dev, y_dev):
        y_pred = self.svm.predict(X_dev)
        acc = (y_pred == y_dev).mean()
        print(f"Dev Accuracy: {acc:.3f}")

    def load_documents(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        documents = []
        labels = []
        for line in lines:
            obj = json.loads(line)
            documents.append(obj['text'])
            labels.append(obj['label'])
        return documents, labels

    def run(self):
        train_docs, train_labels = self.load_documents(self.trainingPath)
        dev_docs, dev_labels = self.load_documents(self.devPath)

        self.calculate_training_statistics(train_docs)
        self.fit_tfidf(train_docs, dev_docs)
        self.fit_pca_kmeans()

        label_encoder = LabelEncoder()
        y_train = label_encoder.fit_transform(train_labels)
        y_dev = label_encoder.transform(dev_labels)

        X_train = self.extract_features(train_docs)
        X_dev = self.extract_features(dev_docs)

        self.train_svm(X_train, y_train)
        self.evaluate_model(X_dev, y_dev)

        # Save other models
        with open("models.pkl", "wb") as f:
            pickle.dump({
                'tfidf': self.tfidf,
                'pca': self.pca,
                'kmeans': self.kmeans,
                'mean_doc_wc': self.mean_doc_wc,
                'std_doc_wc': self.std_doc_wc,
                'mean_sent_wc': self.mean_sent_wc,
                'std_sent_wc': self.std_sent_wc,
            }, f)

if __name__ == "__main__":
    model = AutoILR()
    model.run()
