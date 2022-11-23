import csv
from rich.progress import track
from spamdetector import MailAnalyzer
from spamdetector.files import get_files_from_dir


def list_to_csv(l: list, filename: str):
    with open(filename, 'a', newline="") as f:
        writer = csv.writer(f)
        for elem in l:
            writer.writerow(elem)

def file_to_csv(filename: str, output_file: str, is_spam: int, analyzer: MailAnalyzer):
    raw_files = get_files_from_dir(filename)
    datalist = []
    for file in track(raw_files, description=f'Analyzing files from {filename} folder'):
        analysis = analyzer.analyze(file)
        list_analysis = analysis.to_list()
        list_analysis.append(is_spam)
        datalist.append(list_analysis)
    list_to_csv(datalist, output_file)


if __name__ == '__main__':

    with open('conf/word_blacklist.txt', 'r') as f:
        wordlist = f.readlines()

    analysis_factory = MailAnalyzer(wordlist)

    file_to_csv('dataset/2003_spam', 'dataset/spam.csv', 1, analysis_factory)
    file_to_csv('dataset/2003_easy_ham', 'dataset/spam.csv', 0, analysis_factory)
    file_to_csv('dataset/20021010_hard_ham/hard_ham', 'dataset/spam.csv', 0, analysis_factory)
    file_to_csv('dataset/20030228_spam_2/spam_2', 'dataset/spam.csv', 1, analysis_factory)
    file_to_csv('dataset/20030228_hard_ham/hard_ham', 'dataset/spam.csv', 0, analysis_factory)
