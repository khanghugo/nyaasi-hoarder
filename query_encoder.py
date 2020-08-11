class query_encoder:
    def __init__(self, name):
        self.name = name

        self.query_dict = {
            '%': '%25', # all the `%` must be replaced first or the characters later will be replaced by this
    	    ' ': '%20',
    	    '!': '%21',
    	    '"': '%22',
            '#': '%23',
            '$': '%24',
    	    '&': '%26',
    	    "'": '%27',
    	    '(': '%28',
    	    ')': '%29',
    	    '*': '%2A',
    	    '+': '%2B',
    	    ',': '%2C',
    	    '-': '%2D',
    	    '.': '%2E',
    	    '/': '%2F',
    	    ':': '%3A',
            ';': '%3B',
            '=': '%3D',
    	    '?': '%3F',
    	    '@': '%40',
    	    '[': '%5B',
    	    ']': '%5D',
    	    '\\': '%5C',
    	    '^': '%5E',
    	    '_': '%5F',
    	    '`': '%60',
    	    '~': '%7E'}

    def name_to_query(self):
        for i in self.query_dict:
            if i in self.name:
                self.name = self.name.replace(i, self.query_dict[i])
    
        return self.name