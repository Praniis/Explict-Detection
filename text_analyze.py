from datetime import datetime
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
from explict_check import predict_prob


def processText(pageText):
    soup = BeautifulSoup(pageText, 'html.parser')
    TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'div']
    paragraph = ' '.join([tag.text for tag in soup.findAll(TAGS)])
    tokenizedParagraph = ' '.join(word_tokenize(paragraph))
    sentences = sent_tokenize(tokenizedParagraph)
    windowSize = 1000
    pageSentenceScores = []
    for i, j in enumerate(range(0, len(sentences), windowSize)):
        selected = sentences[j: j + windowSize]
        
        scales = predict_prob(selected)
        
        for index, sentence in enumerate(selected):
            pageSentenceScore = {
                'text': sentence,
                'score': scales[index]
            }
            pageSentenceScores.append(pageSentenceScore)
    return pageSentenceScores
