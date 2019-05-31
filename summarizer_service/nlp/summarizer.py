import re

import numpy as np

from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

from nlp.constants import Constants


def get_sentances(text):
    text = text.replace('\n', '. ')
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(Constants.PREFIXES, "\\1<prd>", text)
    text = re.sub(Constants.WEBSITES, "<prd>\\1", text)
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + Constants.ALPHABETS + "[.] ", " \\1<prd> ", text)
    text = re.sub(Constants.ACRONYMS + " " + Constants.STARTERS, "\\1<stop> \\2", text)
    text = re.sub(Constants.ALPHABETS + "[.]" + Constants.ALPHABETS + "[.]" + Constants.ALPHABETS + "[.]",
                  "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(Constants.ALPHABETS + "[.]" + Constants.ALPHABETS + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + Constants.SUFFIXES + "[.] " + Constants.STARTERS, " \\1<stop> \\2", text)
    text = re.sub(" " + Constants.SUFFIXES + "[.]", " \\1<prd>", text)
    text = re.sub(" " + Constants.ALPHABETS + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def get_site_text(html):
    # html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def check_joined_words(sent):
    return any([len(word) > Constants.WORD_TRESH for word in sent.split(' ')])


def filter_sentances(sentances):
    sentances = [sent for sent in sentances if not check_joined_words(sent)]
    sentances = [sent for sent in sentances if len(sent.split(' ')) > Constants.SENT_TRESH_INITIAL]
    sentances = [sent for sent in sentances if 'highlight' not in sent]
    return sentances


def filter_after_tfidf(sentances, vectors):
    vectors = np.squeeze(np.array([vec for vec, sent in zip(vectors, sentances) if len(sent) > Constants.SENT_TRESH_FINAL]))
    sentances = [sent for sent in sentances if len(sent) > Constants.SENT_TRESH_FINAL]
    return sentances, vectors


def clean_sentances(sentances):
    return [sent.lower() for sent in sentances]


def get_tfidf_sent_vector(sentances):
    tfidf_word = TfidfVectorizer(ngram_range=(1, 4), min_df=2, binary=False)
    tfidf_char = TfidfVectorizer(ngram_range=(2, 5), min_df=5, binary=False, analyzer='char', max_features=500)
    text_vectorizer = FeatureUnion([('word', tfidf_word), ('char', tfidf_char)])

    return text_vectorizer.fit_transform(sentances).todense()


def get_centroids(sent_vectors, num_centroids=5):
    kmeans = KMeans(n_clusters=num_centroids, random_state=0).fit(sent_vectors)
    return kmeans.cluster_centers_


def get_main_sentances(sent_vectors, centroids, site_sentances):
    main_sentances = []
    for centr in centroids:
        sent_idx = np.argmin([np.linalg.norm(centr - vec) for vec in sent_vectors])
        main_sentances.append(site_sentances[sent_idx])

    return list(set(main_sentances))


def summarize_pipeline(html, n_sent=5):
    site_text = get_site_text(html)
    site_sentances = get_sentances(site_text)

    site_sentances = filter_sentances(site_sentances)
    site_sentances = clean_sentances(site_sentances)

    site_sent_vectors = get_tfidf_sent_vector(site_sentances)
    site_sentances, site_sent_vectors = filter_after_tfidf(site_sentances, site_sent_vectors)
    site_centroids = get_centroids(site_sent_vectors, n_sent)

    summary = get_main_sentances(site_sent_vectors, site_centroids, site_sentances)

    return ('\n').join(summary)
