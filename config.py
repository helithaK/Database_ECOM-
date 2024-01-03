from configparser import ConfigParser

def config(filename = "database.ini", section = "postgresql"):
    #Create filename
    parser = ConfigParser()
    #read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        #the config items are added into a dictionary
        for param in params:
            db[param[0]] = param[1]
    else:
        #Raise an exception if the .ini file is not available
        raise Exception('Section{0} is not found in the {1} file. '.format(section, filename))
    #Return the db dictionary with all the config details
    return db

    print(db)

config()


