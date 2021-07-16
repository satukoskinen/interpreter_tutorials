# Token types

INTEGER = "INTEGER"
PLUS = "PLUS"
EOF = "EOF"

class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, EOF
        self.type = type
        # token value: ['0'-'9'], '+', None
        self.value = value
        
    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
        """
        return "Token({type}, {value})".format(type=self.type,value=repr(self.value))

    def __repr__(self):
        return self.__str__()

class Interpreter(object):
    def __init__(self, text):
        # client string input, e.g. "3+5"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        # current token instance
        self.current_token = None
        self.current_char = self.text[self.pos]
        
    def error(self):
        raise Exception("Error parsing input")

    def advance(self):
        self.pos += 1
        if self.pos == len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def integer(self):
        value_start = self.pos
        while self.pos < len(self.text) and self.current_char.isdigit():
            self.advance()
        result = self.text[value_start:self.pos]
        return int(result)
    
    def get_next_token(self):
        """Lexical analyzer (scanner / tokenizer)

        This method is responsible for breaking a sentence apart into tokens,
        one token at a time.
        """
        while self.pos < len(self.text) and self.current_char.isspace():
            self.advance()

        if self.pos == len(self.text):
            return Token(EOF, None)

        if self.current_char.isdigit():
            return Token(INTEGER, self.integer())
        elif self.current_char == '+':
            self.advance()
            return Token(PLUS, self.current_char)
        else:
            self.error()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self):
        self.current_token = self.get_next_token()

        left = self.current_token
        self.eat(INTEGER)

        op = self.current_token
        self.eat(PLUS)

        right = self.current_token
        self.eat(INTEGER)

        result = left.value + right.value
        return result

def main():
    while True:
        try:
            text = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)

if __name__ == "__main__":
    main()
