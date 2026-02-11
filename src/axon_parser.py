"""
AXON Parser — Reference Implementation
Agent eXchange Optimized Notation

A recursive descent parser for the AXON language specification v0.1.
Validates and parses AXON messages into structured Python objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ── Token Types ──────────────────────────────────────────────────────

class TokenType(Enum):
    PERFORMATIVE = "PERFORMATIVE"
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    LBRACE = "{"
    RBRACE = "}"
    COLON = ":"
    COMMA = ","
    ARROW = "->"
    BACKARROW = "<-"
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    NEQ = "!="
    EQ = "="
    AMP = "&"
    PIPE = "|"
    BANG = "!"
    QUESTION = "?"
    TILDE = "~"
    CARET = "^"
    STAR = "*"
    UNDERSCORE = "_"
    DOTDOT = ".."
    DOT = "."
    DOUBLE_PERCENT = "%%"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    REF = "REF"
    TAG = "TAG"
    VAR = "VAR"
    IDENT = "IDENT"
    UNIT = "UNIT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


PERFORMATIVES = {
    "INF", "QRY", "RPL", "CFM", "DNY", "ERR",
    "REQ", "CMD", "PRO", "ACC", "REJ", "CTR", "DEL", "CAN",
    "SUB", "UNS", "PUB", "ACK", "NAK", "SYN",
}

UNITS = {
    "%", "ms", "s", "min", "h", "d",
    "B", "KB", "MB", "GB",
    "tok", "usd", "eur",
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int


# ── Lexer ────────────────────────────────────────────────────────────

class LexerError(Exception):
    def __init__(self, msg: str, line: int, col: int):
        super().__init__(f"Lexer error at {line}:{col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []

    def _peek(self) -> str | None:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def _peek_at(self, offset: int) -> str | None:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _emit(self, ttype: TokenType, value: str, line: int, col: int):
        self.tokens.append(Token(ttype, value, line, col))

    def _read_string(self) -> str:
        result = []
        self._advance()  # consume opening "
        while self.pos < len(self.source):
            ch = self._peek()
            if ch == "\\":
                self._advance()
                esc = self._advance()
                if esc == "n":
                    result.append("\n")
                elif esc == "t":
                    result.append("\t")
                elif esc == '"':
                    result.append('"')
                elif esc == "\\":
                    result.append("\\")
                else:
                    result.append(esc)
            elif ch == '"':
                self._advance()
                return "".join(result)
            else:
                result.append(self._advance())
        raise LexerError("Unterminated string", self.line, self.col)

    def _read_number(self) -> str:
        start = self.pos
        if self._peek() == "-":
            self._advance()
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self._advance()
        if self.pos < len(self.source) and self.source[self.pos] == ".":
            # Don't consume ".." (range operator)
            if self._peek_at(1) == ".":
                return self.source[start:self.pos]
            # Only consume decimal point if followed by a digit
            if self._peek_at(1) is not None and self._peek_at(1).isdigit():
                self._advance()
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self._advance()
        return self.source[start:self.pos]

    def _read_identifier(self) -> str:
        start = self.pos
        while self.pos < len(self.source) and (
            self.source[self.pos].isalnum()
            or self.source[self.pos] == "_"
            or (self.source[self.pos] == "-"
                and self._peek_at(1) != ">")
        ):
            self._advance()
        return self.source[start:self.pos]

    def _read_qualified_id(self) -> str:
        """Read identifier { '.' identifier } for @refs, #tags, $vars."""
        result = self._read_identifier()
        while (self.pos < len(self.source)
               and self.source[self.pos] == "."
               and self._peek_at(1) is not None
               and self._peek_at(1) != "."
               and (self._peek_at(1).isalpha() or self._peek_at(1) == "_")):
            self._advance()  # consume "."
            result += "." + self._read_identifier()
        return result

    def _try_read_unit(self):
        """Try to read a unit suffix after a number."""
        if self.pos >= len(self.source):
            return
        for unit in sorted(UNITS, key=len, reverse=True):
            end = self.pos + len(unit)
            if self.source[self.pos:end] == unit:
                # Don't consume % if followed by % (it's the %% meta token)
                if unit == "%" and end < len(self.source) and self.source[end] == "%":
                    continue
                # Don't consume unit if followed by alphanumeric (part of longer word)
                if end < len(self.source) and (self.source[end].isalnum() or self.source[end] == "_"):
                    continue
                uline, ucol = self.line, self.col
                for _ in unit:
                    self._advance()
                self._emit(TokenType.UNIT, unit, uline, ucol)
                return

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.source):
            ch = self._peek()
            line, col = self.line, self.col

            if ch in " \t\r":
                self._advance()
                continue

            # Comments: (* ... *) — but not (*> which is routing with wildcard
            if ch == "(" and self._peek_at(1) == "*" and self._peek_at(2) != ">":
                self._advance()
                self._advance()
                depth = 1
                while self.pos < len(self.source) and depth > 0:
                    if self.source[self.pos] == "*" and self._peek_at(1) == ")":
                        depth -= 1
                        self._advance()
                        self._advance()
                    elif self.source[self.pos] == "(" and self._peek_at(1) == "*":
                        depth += 1
                        self._advance()
                        self._advance()
                    else:
                        self._advance()
                continue

            if ch == "\n":
                self._advance()
                self._emit(TokenType.NEWLINE, "\n", line, col)
                continue

            if ch == '"':
                s = self._read_string()
                self._emit(TokenType.STRING, s, line, col)
                continue

            # Two-character operators (order matters: check longest first)
            if ch == "-" and self._peek_at(1) == ">":
                self._advance()
                self._advance()
                self._emit(TokenType.ARROW, "->", line, col)
                continue

            if ch == "<" and self._peek_at(1) == "-":
                self._advance()
                self._advance()
                self._emit(TokenType.BACKARROW, "<-", line, col)
                continue

            if ch == "<" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self._emit(TokenType.LTE, "<=", line, col)
                continue

            if ch == ">" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self._emit(TokenType.GTE, ">=", line, col)
                continue

            if ch == "!" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self._emit(TokenType.NEQ, "!=", line, col)
                continue

            if ch == "." and self._peek_at(1) == ".":
                self._advance()
                self._advance()
                self._emit(TokenType.DOTDOT, "..", line, col)
                continue

            if ch == "%" and self._peek_at(1) == "%":
                self._advance()
                self._advance()
                self._emit(TokenType.DOUBLE_PERCENT, "%%", line, col)
                continue

            # Numbers (including negative)
            if ch.isdigit() or (ch == "-" and self._peek_at(1) is not None and self._peek_at(1).isdigit()):
                num = self._read_number()
                self._emit(TokenType.NUMBER, num, line, col)
                self._try_read_unit()
                continue

            # References @qualified.id
            if ch == "@":
                self._advance()
                ident = self._read_qualified_id()
                self._emit(TokenType.REF, "@" + ident, line, col)
                continue

            # Tags #qualified.id
            if ch == "#":
                self._advance()
                ident = self._read_qualified_id()
                self._emit(TokenType.TAG, "#" + ident, line, col)
                continue

            # Variables $qualified.id
            if ch == "$":
                self._advance()
                ident = self._read_qualified_id()
                self._emit(TokenType.VAR, "$" + ident, line, col)
                continue

            # Underscore (null literal)
            if ch == "_":
                self._advance()
                self._emit(TokenType.UNDERSCORE, "_", line, col)
                continue

            # Identifiers, performatives, booleans
            if ch.isalpha():
                ident = self._read_identifier()
                if ident in PERFORMATIVES:
                    self._emit(TokenType.PERFORMATIVE, ident, line, col)
                elif ident in ("T", "F"):
                    self._emit(TokenType.BOOLEAN, ident, line, col)
                else:
                    self._emit(TokenType.IDENT, ident, line, col)
                continue

            # Single-character tokens
            simple = {
                "(": TokenType.LPAREN, ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
                "{": TokenType.LBRACE, "}": TokenType.RBRACE,
                ":": TokenType.COLON, ",": TokenType.COMMA,
                ">": TokenType.GT, "<": TokenType.LT,
                "&": TokenType.AMP, "|": TokenType.PIPE,
                "!": TokenType.BANG, "?": TokenType.QUESTION,
                "~": TokenType.TILDE, "^": TokenType.CARET,
                "=": TokenType.EQ, ".": TokenType.DOT,
                "*": TokenType.STAR,
            }
            if ch in simple:
                self._advance()
                self._emit(simple[ch], ch, line, col)
                continue

            raise LexerError(f"Unexpected character: {ch!r}", line, col)

        self._emit(TokenType.EOF, "", self.line, self.col)
        return self.tokens


# ── AST Nodes ────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    pass

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class NumberLiteral(ASTNode):
    value: float
    unit: str | None = None

@dataclass
class BooleanLiteral(ASTNode):
    value: bool

@dataclass
class NullLiteral(ASTNode):
    pass

@dataclass
class Reference(ASTNode):
    name: str

@dataclass
class Tag(ASTNode):
    name: str
    body: ASTNode | None = None

@dataclass
class Variable(ASTNode):
    name: str

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class ListExpr(ASTNode):
    elements: list[ASTNode]

@dataclass
class RecordExpr(ASTNode):
    fields: dict[str, ASTNode]

@dataclass
class RangeExpr(ASTNode):
    start: ASTNode
    end: ASTNode

@dataclass
class CallExpr(ASTNode):
    func: str
    args: list[ASTNode]

@dataclass
class NamedArg(ASTNode):
    name: str
    value: ASTNode

@dataclass
class BinaryExpr(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class PathExpr(ASTNode):
    parts: list[str]

@dataclass
class Routing(ASTNode):
    sender: str | list[str]
    receiver: str | list[str]

@dataclass
class MetaBlock(ASTNode):
    fields: dict[str, ASTNode]

@dataclass
class Message(ASTNode):
    performative: str
    routing: Routing
    content: ASTNode
    meta: MetaBlock | None = None


# ── Parser ───────────────────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, msg: str, token: Token):
        super().__init__(f"Parse error at {token.line}:{token.col}: {msg} (got {token.type.value}: {token.value!r})")
        self.token = token


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.NEWLINE,)]
        self.pos = 0

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _peek_at(self, offset: int) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, ttype: TokenType) -> Token:
        tok = self._advance()
        if tok.type != ttype:
            raise ParseError(f"Expected {ttype.value}", tok)
        return tok

    def _match(self, ttype: TokenType) -> Token | None:
        if self._peek().type == ttype:
            return self._advance()
        return None

    # ── Top-level ────────────────────────────────────────────────────

    def parse(self) -> list[Message]:
        messages = []
        while self._peek().type != TokenType.EOF:
            messages.append(self._parse_message())
        return messages

    def _is_performative_start(self) -> bool:
        if self._peek().type == TokenType.PERFORMATIVE:
            return True
        # Extension: X.domain.act(
        if (self._peek().type == TokenType.IDENT
            and self._peek().value == "X"
            and self._peek_at(1).type == TokenType.DOT
            and self._peek_at(2).type == TokenType.IDENT
            and self._peek_at(3).type == TokenType.DOT
            and self._peek_at(4).type == TokenType.IDENT
            and self._peek_at(5).type == TokenType.LPAREN):
            return True
        return False

    def _parse_performative(self) -> str:
        if self._peek().type == TokenType.PERFORMATIVE:
            return self._advance().value
        # Extension: X.domain.act
        self._advance()  # X
        self._expect(TokenType.DOT)
        domain = self._expect(TokenType.IDENT)
        self._expect(TokenType.DOT)
        act = self._expect(TokenType.IDENT)
        return f"X.{domain.value}.{act.value}"

    def _parse_message(self) -> Message:
        meta = None
        if self._peek().type == TokenType.LBRACKET:
            meta = self._parse_meta()
        perf = self._parse_performative()
        self._expect(TokenType.LPAREN)
        routing = self._parse_routing()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        content = self._parse_expression()
        return Message(performative=perf, routing=routing, content=content, meta=meta)

    # ── Metadata ─────────────────────────────────────────────────────

    def _parse_meta(self) -> MetaBlock:
        self._expect(TokenType.LBRACKET)
        fields = {}
        while self._peek().type != TokenType.RBRACKET:
            if fields:
                self._expect(TokenType.COMMA)
            if self._peek().type == TokenType.CARET:
                key = self._advance().value
            elif self._peek().type == TokenType.DOUBLE_PERCENT:
                key = self._advance().value
            else:
                key = self._expect(TokenType.IDENT).value
            self._expect(TokenType.COLON)
            val = self._parse_expression()
            fields[key] = val
        self._expect(TokenType.RBRACKET)
        return MetaBlock(fields=fields)

    # ── Routing ──────────────────────────────────────────────────────

    def _parse_routing(self) -> Routing:
        sender = self._parse_endpoint()
        self._expect(TokenType.GT)
        receiver = self._parse_endpoint()
        return Routing(sender=sender, receiver=receiver)

    def _parse_endpoint(self) -> str | list[str]:
        if self._peek().type == TokenType.LBRACKET:
            self._advance()
            agents = []
            while self._peek().type != TokenType.RBRACKET:
                if agents:
                    self._expect(TokenType.COMMA)
                ref = self._expect(TokenType.REF)
                agents.append(ref.value)
            self._advance()
            return agents
        elif self._peek().type == TokenType.STAR:
            self._advance()
            return "*"
        ref = self._expect(TokenType.REF)
        return ref.value

    # ── Expressions (precedence-based) ───────────────────────────────
    #
    # Precedence (lowest to highest):
    #   1: <-  (right-associative, causation)
    #   2: ->  (left-associative, sequence)
    #   3: &   (left-associative, parallel)
    #   4: |   (left-associative, disjunction)
    #   5: < > <= >= != =  (non-associative, comparison)
    #   6: ..  (non-associative, range)
    #   7: ~ (prefix), primaries

    def _parse_expression(self) -> ASTNode:
        return self._parse_causal()

    def _parse_causal(self) -> ASTNode:
        parts = [self._parse_sequence()]
        while self._peek().type == TokenType.BACKARROW:
            self._advance()
            parts.append(self._parse_sequence())
        # Right-associate: a <- b <- c = a <- (b <- c)
        result = parts[-1]
        for i in range(len(parts) - 2, -1, -1):
            result = BinaryExpr(op="<-", left=parts[i], right=result)
        return result

    def _parse_sequence(self) -> ASTNode:
        left = self._parse_parallel()
        while self._peek().type == TokenType.ARROW:
            self._advance()
            right = self._parse_parallel()
            left = BinaryExpr(op="->", left=left, right=right)
        return left

    def _parse_parallel(self) -> ASTNode:
        left = self._parse_disjunction()
        while self._peek().type == TokenType.AMP:
            self._advance()
            right = self._parse_disjunction()
            left = BinaryExpr(op="&", left=left, right=right)
        return left

    def _parse_disjunction(self) -> ASTNode:
        left = self._parse_comparison()
        while self._peek().type == TokenType.PIPE:
            self._advance()
            right = self._parse_comparison()
            left = BinaryExpr(op="|", left=left, right=right)
        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_range()
        comp_ops = {TokenType.LT, TokenType.GT, TokenType.LTE,
                    TokenType.GTE, TokenType.NEQ, TokenType.EQ}
        if self._peek().type in comp_ops:
            op = self._advance()
            right = self._parse_range()
            return BinaryExpr(op=op.value, left=left, right=right)
        return left

    def _parse_range(self) -> ASTNode:
        left = self._parse_primary()
        if self._peek().type == TokenType.DOTDOT:
            self._advance()
            right = self._parse_primary()
            return RangeExpr(start=left, end=right)
        return left

    # ── Primary expressions ──────────────────────────────────────────

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()

        # Prefix ~ (approximate)
        if tok.type == TokenType.TILDE:
            self._advance()
            inner = self._parse_primary()
            return CallExpr(func="~", args=[inner])

        # Nested message
        if self._is_performative_start():
            return self._parse_nested_message()

        # Grouped expression
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        if tok.type == TokenType.LBRACE:
            return self._parse_record()

        if tok.type == TokenType.LBRACKET:
            return self._parse_list()

        if tok.type == TokenType.TAG:
            return self._parse_tag()

        if tok.type == TokenType.IDENT:
            return self._parse_ident_or_call()

        return self._parse_atom()

    def _parse_nested_message(self) -> Message:
        perf = self._parse_performative()
        self._expect(TokenType.LPAREN)
        routing = self._parse_routing()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        content = self._parse_expression()
        return Message(performative=perf, routing=routing, content=content)

    def _parse_atom(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=tok.value)

        if tok.type == TokenType.NUMBER:
            self._advance()
            val = float(tok.value) if "." in tok.value else int(tok.value)
            unit = None
            if self._peek().type == TokenType.UNIT:
                unit = self._advance().value
            return NumberLiteral(value=val, unit=unit)

        if tok.type == TokenType.BOOLEAN:
            self._advance()
            return BooleanLiteral(value=tok.value == "T")

        if tok.type == TokenType.UNDERSCORE:
            self._advance()
            return NullLiteral()

        if tok.type == TokenType.REF:
            self._advance()
            return Reference(name=tok.value)

        if tok.type == TokenType.TAG:
            return self._parse_tag()

        if tok.type == TokenType.VAR:
            self._advance()
            return Variable(name=tok.value)

        if tok.type == TokenType.IDENT:
            return self._parse_ident_or_call()

        raise ParseError("Unexpected token in expression", tok)

    def _parse_tag(self) -> Tag:
        tok = self._advance()
        body = None
        if self._peek().type == TokenType.LBRACE:
            body = self._parse_record()
        return Tag(name=tok.value, body=body)

    def _parse_ident_or_call(self) -> ASTNode:
        tok = self._advance()
        if self._peek().type == TokenType.DOT:
            parts = [tok.value]
            while self._peek().type == TokenType.DOT:
                self._advance()
                next_tok = self._peek()
                if next_tok.type in (TokenType.IDENT, TokenType.PERFORMATIVE):
                    parts.append(self._advance().value)
                else:
                    raise ParseError("Expected identifier after '.'", next_tok)
            if self._peek().type == TokenType.LPAREN:
                return self._parse_call_args(".".join(parts))
            return PathExpr(parts=parts)

        if self._peek().type == TokenType.LPAREN:
            return self._parse_call_args(tok.value)

        return Identifier(name=tok.value)

    def _parse_call_args(self, func_name: str) -> CallExpr:
        self._expect(TokenType.LPAREN)
        args = []
        while self._peek().type != TokenType.RPAREN:
            if args:
                self._expect(TokenType.COMMA)
            args.append(self._parse_argument())
        self._expect(TokenType.RPAREN)
        return CallExpr(func=func_name, args=args)

    def _parse_argument(self) -> ASTNode:
        """Parse a function argument: named (ident:expr) or positional."""
        if (self._peek().type == TokenType.IDENT
            and self._peek_at(1).type == TokenType.COLON):
            name = self._advance()
            self._advance()  # consume colon
            value = self._parse_expression()
            return NamedArg(name=name.value, value=value)
        return self._parse_expression()

    def _parse_list(self) -> ListExpr:
        self._expect(TokenType.LBRACKET)
        elements = []
        while self._peek().type != TokenType.RBRACKET:
            if elements:
                self._expect(TokenType.COMMA)
            elements.append(self._parse_expression())
        self._expect(TokenType.RBRACKET)
        return ListExpr(elements=elements)

    def _parse_record(self) -> RecordExpr:
        self._expect(TokenType.LBRACE)
        fields = {}
        while self._peek().type != TokenType.RBRACE:
            if fields:
                self._expect(TokenType.COMMA)
            key = self._expect(TokenType.IDENT)
            self._expect(TokenType.COLON)
            val = self._parse_expression()
            fields[key.value] = val
        self._expect(TokenType.RBRACE)
        return RecordExpr(fields=fields)


# ── Public API ───────────────────────────────────────────────────────

def parse(source: str) -> list[Message]:
    """Parse AXON source text into a list of Message AST nodes."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def validate(source: str) -> tuple[bool, str]:
    """Validate AXON source text. Returns (is_valid, error_message)."""
    try:
        parse(source)
        return True, "Valid AXON"
    except (LexerError, ParseError) as e:
        return False, str(e)


def format_ast(node: ASTNode, indent: int = 0) -> str:
    """Pretty-print an AST node for debugging."""
    prefix = "  " * indent
    if isinstance(node, Message):
        lines = [f"{prefix}Message({node.performative})"]
        if node.meta:
            lines.append(format_ast(node.meta, indent + 1))
        lines.append(format_ast(node.routing, indent + 1))
        lines.append(f"{prefix}  content:")
        lines.append(format_ast(node.content, indent + 2))
        return "\n".join(lines)
    elif isinstance(node, MetaBlock):
        lines = [f"{prefix}Meta:"]
        for k, v in node.fields.items():
            lines.append(f"{prefix}  {k}: {format_ast(v, 0).strip()}")
        return "\n".join(lines)
    elif isinstance(node, Routing):
        return f"{prefix}Routing({node.sender} > {node.receiver})"
    elif isinstance(node, StringLiteral):
        return f'{prefix}String("{node.value}")'
    elif isinstance(node, NumberLiteral):
        unit = node.unit or ""
        return f"{prefix}Number({node.value}{unit})"
    elif isinstance(node, BooleanLiteral):
        return f"{prefix}Bool({node.value})"
    elif isinstance(node, NullLiteral):
        return f"{prefix}Null"
    elif isinstance(node, Reference):
        return f"{prefix}Ref({node.name})"
    elif isinstance(node, Tag):
        if node.body:
            return f"{prefix}Tag({node.name})\n{format_ast(node.body, indent + 1)}"
        return f"{prefix}Tag({node.name})"
    elif isinstance(node, Variable):
        return f"{prefix}Var({node.name})"
    elif isinstance(node, ListExpr):
        if not node.elements:
            return f"{prefix}List([])"
        lines = [f"{prefix}List(["]
        for el in node.elements:
            lines.append(format_ast(el, indent + 1))
        lines.append(f"{prefix}])")
        return "\n".join(lines)
    elif isinstance(node, RecordExpr):
        lines = [f"{prefix}Record({{"]
        for k, v in node.fields.items():
            lines.append(f"{prefix}  {k}: {format_ast(v, 0).strip()}")
        lines.append(f"{prefix}}})")
        return "\n".join(lines)
    elif isinstance(node, RangeExpr):
        return f"{prefix}Range({format_ast(node.start, 0).strip()}..{format_ast(node.end, 0).strip()})"
    elif isinstance(node, CallExpr):
        args = ", ".join(format_ast(a, 0).strip() for a in node.args)
        return f"{prefix}Call({node.func}({args}))"
    elif isinstance(node, NamedArg):
        return f"{prefix}{node.name}: {format_ast(node.value, 0).strip()}"
    elif isinstance(node, BinaryExpr):
        return f"{prefix}BinOp({format_ast(node.left, 0).strip()} {node.op} {format_ast(node.right, 0).strip()})"
    elif isinstance(node, PathExpr):
        return f"{prefix}Path({'.'.join(node.parts)})"
    elif isinstance(node, Identifier):
        return f"{prefix}Ident({node.name})"
    return f"{prefix}Unknown({type(node).__name__})"


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    import sys

    if len(sys.argv) < 2:
        print("AXON Parser v0.1")
        print("Usage: python axon_parser.py <file.axon>     Parse and validate")
        print("       python axon_parser.py --ast <file>    Show AST")
        print("       python axon_parser.py --check <file>  Validate only")
        print()
        print("Or pipe AXON text via stdin:")
        print('  echo \'QRY(@a>@b): status(@server)\' | python axon_parser.py -')
        sys.exit(0)

    show_ast = "--ast" in sys.argv
    check_only = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args:
        print("Error: No input file specified")
        sys.exit(1)

    filename = args[0]
    if filename == "-":
        source = sys.stdin.read()
    else:
        with open(filename) as f:
            source = f.read()

    if check_only:
        valid, msg = validate(source)
        print(msg)
        sys.exit(0 if valid else 1)

    try:
        messages = parse(source)
        print(f"Parsed {len(messages)} message(s) successfully.\n")
        if show_ast:
            for i, msg in enumerate(messages):
                print(f"── Message {i + 1} ──")
                print(format_ast(msg))
                print()
        else:
            for i, msg in enumerate(messages):
                perf = msg.performative
                r = msg.routing
                sender = r.sender if isinstance(r.sender, str) else ",".join(r.sender)
                receiver = r.receiver if isinstance(r.receiver, str) else ",".join(r.receiver)
                print(f"  [{i + 1}] {perf}({sender}>{receiver})")
    except (LexerError, ParseError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
