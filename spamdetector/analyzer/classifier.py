import pickle
from sklearn.tree import DecisionTreeClassifier

class SpamClassifier:
    def __init__(self, X_train, y_train):
        self.clf = DecisionTreeClassifier()
        self.clf.fit(X_train, y_train)

    def predict(self, X_test):
        return self.clf.predict(X_test)

def save_model(model: SpamClassifier, path: str) -> None:
    with open(path, 'wb') as f:
        pickle.dump(model, f)

def load_model(path: str) -> SpamClassifier:
    with open(path, 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    import pandas as pd
    
    df = pd.read_csv('dataset/spam.csv')
    
    X = df.drop(['is_spam', 'Unnamed: 3', 'Unnamed: 4'], axis=1)
    y = df['is_spam']
    
    model = SpamClassifier(X, y)
    save_model(model, 'classifier.pkl')