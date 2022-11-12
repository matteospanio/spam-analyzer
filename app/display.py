import termtables as tt

COLORS = {
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
}

HEADER = [
    'File',
    'Domain',
    'SPF',
    'DKIM',
    'DMARC',
    'Auth Warning',
    'has spam word',
    'script',
    'http link',
    'Trust'
]

def summary(data):
    warn = 0
    spam = 0
    trust = 0
    for row in data:
        if row[1] is True:
            row[1] = '\033[1;32m' + str(row[1]) + '\033[0;0m'
        if row[2] is True:
            row[2] = '\033[1;32m' + str(row[2]) + '\033[0;0m'
        if row[1] is False and row[2] is False:
            row[1] = '\033[1;31m' + str(row[1]) + '\033[0;0m'
            row[2] = '\033[1;31m' + str(row[2]) + '\033[0;0m'
        if row[3] is True:
            row[3] = '\033[1;32m' + str(row[3]) + '\033[0;0m'

        if row[4] is True:
            row[4] = '\033[1;32m' + str(row[4]) + '\033[0;0m'

        if row[5] is True:
            row[5] = '\033[1;31m' + str(row[5]) + '\033[0;0m'
        if row[5] is False:
            row[5] = '\033[1;32m' + str(row[5]) + '\033[0;0m'
        if row[6] is True:
            row[6] = '\033[1;31m' + str(row[6]) + '\033[0;0m'
        if row[6] is False:
            row[6] = '\033[1;32m' + str(row[6]) + '\033[0;0m'
        if row[7] is True:
            row[7] = '\033[1;31m' + str(row[7]) + '\033[0;0m'
        if row[7] is False:
            row[7] = '\033[1;32m' + str(row[7]) + '\033[0;0m'
        if row[8] is True:
            row[8] = '\033[1;31m' + str(row[8]) + '\033[0;0m'
        if row[8] is False:
            row[8] = '\033[1;32m' + str(row[8]) + '\033[0;0m'
        if row[9] == 'Trust':
            row[9] = '\033[1;32m' + str(row[9]) + '\033[0;0m'
            trust += 1
        if row[9] == 'Warning':
            row[9] = '\033[1;33m' + str(row[9]) + '\033[0;0m'
            warn += 1
        if row[9] == 'Spam':
            row[9] = '\033[1;31m' + str(row[9]) + '\033[0;0m'
            spam += 1

    tt.print(data, header=HEADER, style=tt.styles.rounded)
    print(f'{spam} out of {len(data)} emails are spam')
    print(f'{warn} out of {len(data)} emails raised a warning')
    print(f'{trust} out of {len(data)} emails are trustable')

def short(data):
    warn = 0
    spam = 0
    trust = 0
    short_data = []
    for row in data:
        if row[-1] == 'Trust':
            row[-1] = '\033[1;32m' + str(row[-1]) + '\033[0;0m'
            trust += 1
        if row[-1] == 'Warning':
            row[-1] = '\033[1;33m' + str(row[-1]) + '\033[0;0m'
            warn += 1
        if row[-1] == 'Spam':
            row[-1] = '\033[1;31m' + str(row[-1]) + '\033[0;0m'
            spam += 1
        short_data.append([row[0], row[-1]])

    tt.print(short_data, header=['File', 'Trust'])
    print(f'{spam} out of {len(data)} emails are spam')
    print(f'{warn} out of {len(data)} emails raised a warning')
    print(f'{trust} out of {len(data)} emails are trustable')
