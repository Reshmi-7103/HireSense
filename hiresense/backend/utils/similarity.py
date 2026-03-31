from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(resume_text, job_descriptions):
    """
    resume_text: cleaned resume text (string)
    job_descriptions: list of cleaned job descriptions
    """

    corpus = [resume_text] + job_descriptions

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )

    return similarity_scores.flatten()
