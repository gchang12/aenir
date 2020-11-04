def gender_dict(game):
    from os.path import sep

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

if __name__=='__main__':
    k=8
    game=str(k)
    x=gender_dict(game)
    for item in x.items():
        print(item)
