



class ReversibleString:
    def __init__(self, string):
        self.string = string
    
    def __neg__(self) -> "ReversibleString":
        return self.__class__(self.string[::-1])

    def __str__(self):
        return self.string
        

# print(list('\nfasdfasdf\n\n\nasdfasdf\n'.rstrip()))