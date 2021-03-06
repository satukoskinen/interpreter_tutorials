# The program is made up of three classes:
#
# 1) Lexer
# - takes the source file's text as input
# - splits the input text into tokens
# 2) Parser
# - takes the lexer as input and calls it to retrieve the tokens to process
# - parses the stream of tokens according to the grammar to produce a parse tree
# 3) Interpreter
# - traverses the tree produced by the parser, visits and executes each of the nodes


## LEXER

# Token types
(PROGRAM, PROCEDURE, VAR, INTEGER, REAL, INTEGER_CONST, REAL_CONST, LPAREN, RPAREN, PLUS, MINUS, MUL, FLOAT_DIV, INTEGER_DIV, ID, ASSIGN, BEGIN, END, SEMI, COLON, COMMA, DOT, EOF) = (
    "PROGRAM", "PROCEDURE", "VAR", "INTEGER", "REAL", "INTEGER_CONST", "REAL_CONST", "(", ")", "PLUS", "MINUS", "MUL", "FLOAT_DIV", "INTEGER_DIV", "ID", "ASSIGN", "BEGIN", "END", "SEMI", "COLON", "COMMA", "DOT", "EOF"
    )


class Token(object):
    def __init__(self, type, value):
        # token type
        self.type = type
        # token value
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


RESERVED_KEYWORDS = {
    "PROGRAM": Token("PROGRAM", "PROGRAM"),
    "VAR": Token("VAR", "VAR"),
    "DIV": Token("INTEGER_DIV", "DIV"),
    "INTEGER": Token("INTEGER", "INTEGER"),
    "REAL": Token("REAL", "REAL"),
    "BEGIN": Token("BEGIN", "BEGIN"),
    "END": Token("END", "END"),
    "PROCEDURE": Token("PROCEDURE", "PROCEDURE"),
}


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

    def peek(self):
        """Peek at the next character without consuming it"""
        peek_pos = self.pos + 1
        if peek_pos == len(self.text):
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()

    def number(self):
        """Return a multidigit integer or float consumed from the input"""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()
            token = Token("REAL_CONST", float(result))
        else:
            token = Token("INTEGER_CONST", int(result))
        return token

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char.upper()
            self.advance()
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        """Lexical analyzer

        Responsible for breaking a sentence into tokens"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            elif self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            elif self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            elif self.current_char.isdigit():
                return self.number()
            elif self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ":=")
            elif self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')
            elif self.current_char == ':':
                self.advance()
                return Token(COLON, ':')
            elif self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
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
                return Token(FLOAT_DIV, '/')
            elif self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            elif self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            elif self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            else:
                self.error()
    
        if self.current_char is None:
            return Token(EOF, None)


## PARSER

class AST(object):
    pass

class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class ProcedureDecl(AST):
    def __init__(self, proc_name, block_node):
        self.proc_name = proc_name
        self.block_node = block_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Compound(AST):
    """Represents a 'BEGIN...END' block"""
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """The Var node is constructed out of ID token"""
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token in the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, token_type):
        # print(self.current_token)
        # print(token_type)
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        """program : PROGRAM variable SEMI block DOT"""
        self.eat(PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.eat(DOT)
        return program_node

    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        """declarations : VAR (variable_declaration SEMI)+
                        | (PROCEDURE ID SEMI block SEMI)*
                        | empty
        """
        declarations = []
        while self.current_token.type == VAR or self.current_token.type == PROCEDURE:
            while self.current_token.type == VAR:
                self.eat(VAR)
                while self.current_token.type == ID:
                    var_decl = self.variable_declaration()
                    declarations.extend(var_decl)
                    self.eat(SEMI)
            
            while self.current_token.type == PROCEDURE:
                self.eat(PROCEDURE)
                proc_name = self.current_token.value
                self.eat(ID)
                self.eat(SEMI)
                block_node = self.block()
                proc_decl = ProcedureDecl(proc_name, block_node)
                declarations.append(proc_decl)
                self.eat(SEMI)
        
        return declarations

    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [ Var(self.current_token) ] #first ID
        self.eat(ID)

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)
        
        self.eat(COLON)

        type_node = self.type_spec()
        var_declarations = [
            VarDecl(var_node, type_node) for var_node in var_nodes
        ]
        return var_declarations

    def type_spec(self):
        """type_spec : INTEGER
                      | REAL
        """
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node

    def compound_statement(self):
        """compound_statement : BEGIN statement_list END"""
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        """statement_list : statement
                            | statement SEMI statement_list
        """
        node = self.statement()
        results = [node]

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())
        
        # if self.current_token.type == ID:
        #     self.error()
        return results

    def statement(self):
        """statement : compound_statement
                        | assignment_statemwent
                        | empty
        """
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """variable : ID"""
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """an empty production"""
        return NoOp()

    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)
            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                    | MINUS factor
                    | INTEGER_CONST
                    | REAL_CONST
                    | LPAREN expr RPAREN
                    | variable
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        """
        program : PROGRAM variable SEMI block DOT
        block : declarations compound_statement
        declarations : VAR (variable_declaration SEMI)+
                      | (PROCEDURE ID SEMI block SEMI)*
                      | empty
        variable_declaration : ID (COMMA ID)* COLON type_spec
        type_spec : INTEGER | REAL
        compound_statement : BEGIN statement_list END
        statement_list : statement
                       | statement SEMI statement_list
        statement : compound_statement
                  | assignment_statement
                  | empty
        assignment_statement : variable ASSIGN expr
        empty :
        expr: term ((PLUS | MINUS) term)*
        term: factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*
        factor : PLUS factor
               | MINUS factor
               | INTEGER_CONST
               | REAL_CONST
               | LPAREN expr RPAREN
               | variable
        variable: ID
        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node


## INTERPRETER

class NodeVisitor(object):
    def visit(self, node):
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception("No visit_{} method".format(type(node).__name__))

class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}

    def __init__(self, tree):
        self.tree = tree

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        pass

    def visit_ProcedureDecl(self, node):
        pass

    def visit_Type(self, node):
        pass
    
    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))


    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val
    
    def visit_NoOp(self, node):
        pass
    
    def interpret(self):
        tree = self.tree
        if tree is None:
            return ""
        return self.visit(tree)


## Symbol table implementation

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name})>".format(
            class_name=self.__class__.__name__,
            name=self.name
        )

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)
    
    def __str__(self):
        return "<{name}:{type}>".format(name=self.name, type=self.type)

    def __repr__(self):
        return "<{class_name}(name='{name}, type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type
        )

class SymbolTable(object):
    def __init__(self):
        self._symbols = dict()
        self._init_builtins()
    
    def _init_builtins(self):
        self.define(BuiltinTypeSymbol("INTEGER"))
        self.define(BuiltinTypeSymbol("REAL"))
        
    def __str__(self):
        symtab_header = 'Symbol table contents'
        lines = ['\n', symtab_header, '_' * len(symtab_header)]
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s
    
    __repr__ = __str__

    def define(self, symbol):
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        symbol = self._symbols.get(name)
        return symbol

class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()
    
    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        
        var_name = node.var_node.value
        if self.symtab.lookup(var_name) is not None:
            raise Exception(
                "Error: Duplicate identifier '{}'".format(var_name)
            )

        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    def visit_ProcedureDecl(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol (identifier) not found '{}'".format(var_name)
            )

        self.visit(node.right)
    
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_UnaryOp(self, node):
        self.visit(node.expr)
    
    def visit_NoOp(self, node):
        pass

    def visit_Num(self, node):
        pass

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)

        if var_symbol is None:
            raise NameError(repr(var_name))

## RUN

def main():
    import sys
    text = open(sys.argv[1], 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()

    # Actually this already constitutes a simple semantic analyzer
    symtab_builder = SymbolTableBuilder()
    symtab_builder.visit(tree)
    print(symtab_builder.symtab)

    interpreter = Interpreter(tree)
    result = interpreter.interpret()
    print("Runtime GLOBAL_SCOPE contents")
    print(interpreter.GLOBAL_SCOPE)

if __name__ == "__main__":
    main()
