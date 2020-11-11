from os.path import sep

def gender_dict(game):
    path_to_genders=('.','metadata','genders.csv')
    gender_file=sep.join(path_to_genders)

    d={}

    with open(gender_file,'r') as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            if line[0] != game:
                if not d:
                    continue
                else:
                    break
            unit=line[1]
            gender=int(line[2])
            if gender == 0:
                x=' (M)'
            elif gender == 1:
                x=' (F)'
            else:
                suffix=' ('+unit+')'
                x=suffix
            d[unit]=x
    return d


def promo_dict(game,is_promo=False):
    promo_file=('.','metadata',r'genders.csv')
    promo_file=sep.join(promo_file)

    d={}

    with open(promo_file) as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            if line[0] != game:
                if not d:
                    continue
                else:
                    break
            unit=line[1]
            promo_path=line[3]
            if is_promo:
                if promo_path == 'NA':
                    x=True
                else:
                    x=False
                d[unit]=x
                continue
            if promo_path.isdigit():
                promo_path=int(promo_path)
                d[unit]=promo_path
    return d


if __name__=='__main__':
    k=8
    game=str(k)
    x=gender_dict(game)
    for item in x.items():
        print(item)
