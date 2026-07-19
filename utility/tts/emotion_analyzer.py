from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_emotion_tag(text):
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    neg = scores['neg']
    pos = scores['pos']
    
    if compound >= 0.6:
        return "[excitedly] "
    elif compound <= -0.5:
        return "[sadly] "
    elif neg > 0.4:
        return "[anxiously] "
    elif pos > 0.4:
        return "[cheerfully] "
    elif "!" in text and compound > 0.2:
        return "[enthusiastically] "
    elif "?" in text:
        return "[curiously] "
    else:
        return "[calmly] "

def add_emotion_tags(script):
    sentences = script.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
    processed = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            tag = get_emotion_tag(sentence)
            processed.append(tag + sentence)
    return ' '.join(processed)
