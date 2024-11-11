class classproperty:
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, cls):
        return self.method(cls)
