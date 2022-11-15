from os import path, listdir

def get_files_from_dir(directory):
    file_list = []
    for filename in listdir(directory):
        mail_path = path.join(directory, filename)
        file_list.append(mail_path)

    return file_list