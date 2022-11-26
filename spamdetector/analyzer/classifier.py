import pickle
import pandas as pd

HEADERS = [
    'has_spf',
    'has_dkim',
    'has_dmarc',
    'domain_matches',
    'auth_warn',
    'has_suspect_subject',
    'subject_is_uppercase',
    'send_date_is_RFC2822_compliant',
    'send_date_tz_is_valid',
    'has_received_date',
    'uppercase_body',
    'script',
    'images',
    'https_only',
    'mailto',
    'links',
    'bad_words_percentage',
    'html',
    'form',
    'polarity',
    'subjectivity',
    'attachments',
    'attach_is_executable',
    'is_spam'
]

class SpamClassifier:

    def __init__(self, path_to_model) -> None:
        self.model = load_model(path_to_model)

    def predict(self, X_test):
        X = pd.DataFrame(X_test, columns=HEADERS[:-1])
        return self.model.predict(X)

def save_model(model: SpamClassifier, path: str) -> None:
    with open(path, 'wb') as f:
        pickle.dump(model, f)

def load_model(path: str):
    with open(path, 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    import pandas as pd
    
    df = pd.read_csv('dataset/spam.csv')
    
    X = df.drop(['is_spam', 'Unnamed: 3', 'Unnamed: 4'], axis=1)
    y = df['is_spam']
    
    model = SpamClassifier(X, y)
    save_model(model, 'classifier.pkl')