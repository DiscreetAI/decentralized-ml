
logging.basicConfig(level=logging.DEBUG,
                    format='[ConfigurationManager] %(asctime)s %(levelname)s %(message)s')

class ConfigurationManager(object):
	__instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ConfigurationManager.__instance == None:
            ConfigurationManager()
        return ConfigurationManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ConfigurationManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ConfigurationManager.__instance = self
