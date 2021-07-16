# Token types
INTEGER, PLUS, MINUS, MUL, DIV, EOF = (
    "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "EOF"
    )

class Token(object):
    def __init__(self, type, value):
        #token type
        self.type = type
        #token value: nonnegative integer, '+', '-', '*', '/' or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Example: Token(INTEGER, 3); Token(PLUS, '+')
        """
        return "Token({type}, {value})".format(
            type=self.type,
            value=repr(self.value)
            )

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, text):
        # client string input
        self.text = text
        # current index in self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception("Invalid character")

    def advance(self):
        """Advance the `pos` pointer and set `current_char`"""
        self.pos += 1
        if self.pos == len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a multidigit integer consumed from the input"""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        """Lexical analyzer

        Responsible for breaking a sentence into tokens"""
        if self.current_char is not None and self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char is None:
            return Token(EOF, None)
        elif self.current_char.isdigit():
            return Token(INTEGER, self.integer())
        elif self.current_char == '+':
            self.advance()
            return Token(PLUS, '+')
        elif self.current_char == '-':
            self.advance()
            return Token(MINUS, '-')
        elif self.current_char == '*':
            self.advance()
            return Token(MUL, '*')
        elif self.current_char == '/':
            self.advance()
            return Token(DIV, '/')
        else:
            self.error()

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token in the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : INTEGER"""
        token = self.current_token
        self.eat(INTEGER)
        return token.value

    def term(self):
        """term: factor ((MUL | DIV) factor)*"""
        result = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                result = result / self.factor()
        return result

    def expr(self):
        """Arithmetic expression parser / interpreter

        Example:
        calc> 14 + 2 * 3 - 6 / 2
        17

        Grammar:
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER
        """
        result = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                result = result + self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                result = result - self.term()

        return result

def main():
    while True:
        try:
            text = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.expr()
        print(result)

if __name__ == "__main__":
    main()
