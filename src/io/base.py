import io

class MyIO(io.TextIOWrapper):

    def __init__(self, buffer):
        super().__init__(buffer, line_buffering=True, encoding='UTF-8')

        
class BufferedIO(MyIO):

    def __init__(self):
        super().__init__(io.BytesIO())

    def readall(self)-> str:
        self.seek(0)
        return self.read()