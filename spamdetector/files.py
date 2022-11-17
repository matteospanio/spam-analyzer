from os import path, listdir
import mailparser

def get_files_from_dir(directory):
    file_list = []
    for filename in listdir(directory):
        mail_path = path.join(directory, filename)
        if file_is_valid_email(mail_path):
            file_list.append(mail_path)
        else:
            print("Invalid file found: {}".format(mail_path))

    return file_list

def file_is_valid_email(file_path):
    mail = mailparser.parse_from_file(file_path)
    return path.isfile(file_path) and mail.headers.get('Received') is not None and mail.headers.get('From') is not None