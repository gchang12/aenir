def scold_user(message,iterable=None):
    if iterable is not None:
        for item in iterable:
            print(item)
    if type(messsage) == str:
        message=('',message,'')
    else:
        message=('',*message,'')
    message='\n'.join(message)
    print(message)
    raise Exception
