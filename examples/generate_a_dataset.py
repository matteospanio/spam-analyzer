import csv, os
from rich.progress import track
from spamanalyzer import MailAnalyzer
from app.files import get_files_from_dir


def list_to_csv(l: list, filename: str):
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        for elem in l:
            writer.writerow(elem)


def file_to_csv(filename: str, output_file: str, is_spam: int, analyzer: MailAnalyzer):
    raw_files = get_files_from_dir(filename)
    datalist = []
    for file in track(raw_files, description=f"Analyzing files from {filename} folder"):
        analysis = analyzer.analyze(file)
        list_analysis = analysis.to_list()
        list_analysis.append(is_spam)
        datalist.append(list_analysis)
    list_to_csv(datalist, output_file)


if __name__ == "__main__":
    with open("conf/word_blacklist.txt", "r") as f:
        wordlist = f.readlines()

    destination = "docs/data/spam.csv"

    analysis_factory = MailAnalyzer(wordlist)

    file_to_csv("dataset/2021/02", destination, 1, analysis_factory)
    file_to_csv("dataset/2021/03", destination, 1, analysis_factory)
    file_to_csv("dataset/2021/04", destination, 1, analysis_factory)
    file_to_csv("dataset/2021/05", destination, 1, analysis_factory)
    file_to_csv("dataset/personale/spam", destination, 1, analysis_factory)
    file_to_csv("dataset/personale/ham", destination, 0, analysis_factory)
    file_to_csv("dataset/2022-10-spam", destination, 1, analysis_factory)
    for folder in os.listdir("dataset/spamassassin_ham"):
        file_to_csv(
            f"dataset/spamassassin_ham/{folder}", destination, 0, analysis_factory
        )
    for folder in os.listdir("dataset/spamassassin_spam"):
        file_to_csv(
            f"dataset/spamassassin_spam/{folder}", destination, 1, analysis_factory
        )
