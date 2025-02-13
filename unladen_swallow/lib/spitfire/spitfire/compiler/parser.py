from __future__ import print_function# Copyright 2007 The Spitfire Authors. All Rights Reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

# This parser can parse a progressively larger set of Cheetah+homemade syntax.

from spitfire.compiler import ast
import sys
if sys.version_info[0] > 2:
    unicode = str

from string import *
import re
from third_party.yapps2.yappsrt import *

class _SpitfireParserScanner(Scanner):
    patterns = [
        ("'[ \\t]*\\+[ \\t]*'", re.compile('[ \t]*\\+[ \t]*')),
        ("'[ \\t]*\\%[ \\t]*'", re.compile('[ \t]*\\%[ \t]*')),
        ("'[ \\t]*\\/[ \\t]*'", re.compile('[ \t]*\\/[ \t]*')),
        ("'[ \\t]*\\*[ \\t]*'", re.compile('[ \t]*\\*[ \t]*')),
        ("'[ \\t]*\\-[ \\t]*'", re.compile('[ \t]*\\-[ \t]*')),
        ('"[ \\t]*not[ \\t]*"', re.compile('[ \t]*not[ \t]*')),
        ("'[ \\t]*and[ \\t]*'", re.compile('[ \t]*and[ \t]*')),
        ("'[ \\t]*or[ \\t]*'", re.compile('[ \t]*or[ \t]*')),
        ('"\\."', re.compile('\\.')),
        ('"False"', re.compile('False')),
        ('"True"', re.compile('True')),
        ('"\'"', re.compile("'")),
        ('\'"\'', re.compile('"')),
        ("'#else'", re.compile('#else')),
        ("'#elif'", re.compile('#elif')),
        ("'strip_lines'", re.compile('strip_lines')),
        ("'for'", re.compile('for')),
        ("'[ \\t]*in[ \\t]*'", re.compile('[ \t]*in[ \t]*')),
        ("'for[ \\t]*'", re.compile('for[ \t]*')),
        ("'def'", re.compile('def')),
        ("'i18n'", re.compile('i18n')),
        ("'block'", re.compile('block')),
        ("'library'", re.compile('library')),
        ("'else'", re.compile('else')),
        ("'if'", re.compile('if')),
        ("'echo'", re.compile('echo')),
        ("'set'", re.compile('set')),
        ("'do'", re.compile('do')),
        ("'filter'", re.compile('filter')),
        ("'attr'", re.compile('attr')),
        ("'global'", re.compile('global')),
        ("'continue'", re.compile('continue')),
        ("'break'", re.compile('break')),
        ("'slurp'", re.compile('slurp')),
        ("'import'", re.compile('import')),
        ("'from'", re.compile('from')),
        ("'allow_undeclared_globals'", re.compile('allow_undeclared_globals')),
        ("'allow_raw'", re.compile('allow_raw')),
        ("'loose_resolution'", re.compile('loose_resolution')),
        ("'absolute_extends'", re.compile('absolute_extends')),
        ("'extends'", re.compile('extends')),
        ("'implements'", re.compile('implements')),
        ('DOT', re.compile('\\.')),
        ('NUM', re.compile('[0-9]+')),
        ('ID', re.compile('[A-Za-z_][0-9A-Za-z_]*')),
        ('SINGLE_QUOTE_STR', re.compile("(?:[^'\\\\]|\\\\.)*")),
        ('DOUBLE_QUOTE_STR', re.compile('(?:[^"\\\\]|\\\\.)*')),
        ('SINGLE_LINE_COMMENT', re.compile('#.*?\n')),
        ('MULTI_LINE_COMMENT', re.compile('\\*[\\W\\w\\S\\s]+?\\*#')),
        ('ASSIGN_OPERATOR', re.compile('=')),
        ('COMP_OPERATOR', re.compile('[ \t]*(<=|>=|==|>|<|!=|[ \t]+in[ \t]+)[ \t]*')),
        ('OPEN_PAREN', re.compile('[ \t]*\\([ \t]*')),
        ('PLACEHOLDER_OPEN_PAREN', re.compile('\\([ \t]*')),
        ('CLOSE_PAREN', re.compile('[ \t]*\\)')),
        ('OPEN_BRACKET', re.compile('[ \t]*\\[[ \t]*')),
        ('CLOSE_BRACKET', re.compile('[ \t]*\\]')),
        ('PLACEHOLDER_OPEN_BRACE', re.compile('\\{[ \t]*')),
        ('PLACEHOLDER_CLOSE_BRACE', re.compile('[ \t]*\\}')),
        ('OPEN_BRACE', re.compile('[ \t]*\\{[ \t]*')),
        ('CLOSE_BRACE', re.compile('[ \t]*\\}[ \t]*')),
        ('PIPE', re.compile('[ \t]*\\|[ \t]*')),
        ('COMMA_DELIMITER', re.compile('[ \t]*,[ \t]*')),
        ('COLON_DELIMITER', re.compile('[ \t]*:[ \t]*')),
        ('SPACE', re.compile('[ \t]+')),
        ('CLOSE_DIRECTIVE_TOKEN', re.compile('[\n#]')),
        ('END_DIRECTIVE', re.compile('#end')),
        ('START_DIRECTIVE', re.compile('#')),
        ('START_PLACEHOLDER', re.compile('\\$')),
        ('LITERAL_DOLLAR_SIGN', re.compile('\\\\\\$')),
        ('LITERAL_HASH', re.compile('\\\\#')),
        ('LITERAL_BACKSLASH', re.compile('\\\\')),
        ('NEWLINE', re.compile('\n')),
        ('PYTHON_LINE', re.compile('.+')),
        ('TEXT', re.compile('[^\\\\#\\$\n]+')),
        ('END', re.compile('$')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,[],str)

class _SpitfireParser(Parser):
    def i18n_body(self):
        value = ''
        while 1:
            _token_ = self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_BACKSLASH', 'TEXT', 'NEWLINE', 'START_PLACEHOLDER')
            if _token_ == 'LITERAL_DOLLAR_SIGN':
                LITERAL_DOLLAR_SIGN = self._scan('LITERAL_DOLLAR_SIGN')
                value += LITERAL_DOLLAR_SIGN
            elif _token_ == 'LITERAL_BACKSLASH':
                LITERAL_BACKSLASH = self._scan('LITERAL_BACKSLASH')
                value += LITERAL_BACKSLASH
            elif _token_ == 'TEXT':
                TEXT = self._scan('TEXT')
                value += TEXT
            elif _token_ == 'NEWLINE':
                NEWLINE = self._scan('NEWLINE')
                value += NEWLINE
            else:# == 'START_PLACEHOLDER'
                START_PLACEHOLDER = self._scan('START_PLACEHOLDER')
                value += START_PLACEHOLDER
            if self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_BACKSLASH', 'TEXT', 'NEWLINE', 'START_PLACEHOLDER', 'START_DIRECTIVE', 'END_DIRECTIVE') not in ['LITERAL_DOLLAR_SIGN', 'LITERAL_BACKSLASH', 'TEXT', 'NEWLINE', 'START_PLACEHOLDER']: break
        return value

    def CLOSE_DIRECTIVE(self):
        if self._peek('SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'SPACE':
            SPACE = self._scan('SPACE')
        CLOSE_DIRECTIVE_TOKEN = self._scan('CLOSE_DIRECTIVE_TOKEN')
        return CLOSE_DIRECTIVE_TOKEN

    def CLOSE_END_DIRECTIVE(self):
        if self._peek('SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") == 'SPACE':
            SPACE = self._scan('SPACE')
        _token_ = self._peek('CLOSE_DIRECTIVE_TOKEN', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'")
        if _token_ == 'CLOSE_DIRECTIVE_TOKEN':
            CLOSE_DIRECTIVE_TOKEN = self._scan('CLOSE_DIRECTIVE_TOKEN')
            return CLOSE_DIRECTIVE_TOKEN
        else:
            _token_ = self._peek('END')
            if _token_ == 'END': return ''

    def goal(self):
        template = ast.TemplateNode()
        while self._peek('END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT') != 'END':
            block = self.block(start=True)
            template.append(block)
        END = self._scan('END')
        return template

    def fragment_goal(self):
        fragment = ast.FragmentNode()
        while self._peek('END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT') != 'END':
            block = self.block(start=True)
            fragment.append(block)
        END = self._scan('END')
        return fragment

    def i18n_goal(self):
        fragment = ast.FragmentNode()
        start_pos = 0
        while self._peek('END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT') != 'END':
            text_or_placeholders = self.text_or_placeholders(start=True)
            end_pos = self._scanner.tokens[self._pos-1][1]
            fragment.append(text_or_placeholders)
            text_or_placeholders.start = start_pos
            text_or_placeholders.end = end_pos
            start_pos = end_pos
        END = self._scan('END')
        return fragment

    def statement(self):
        _token_ = self._peek("'implements'", "'extends'", "'absolute_extends'", "'loose_resolution'", "'allow_raw'", "'allow_undeclared_globals'", "'from'", "'import'", "'slurp'", "'break'", "'continue'", "'global'", "'attr'", "'filter'", "'do'", "'set'", "'echo'")
        if _token_ == "'implements'":
            self._scan("'implements'")
            SPACE = self._scan('SPACE')
            ID = self._scan('ID')
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.ImplementsNode(ID)
        elif _token_ == "'extends'":
            self._scan("'extends'")
            SPACE = self._scan('SPACE')
            modulename = self.modulename()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.ExtendsNode(modulename)
        elif _token_ == "'absolute_extends'":
            self._scan("'absolute_extends'")
            SPACE = self._scan('SPACE')
            modulename = self.modulename()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.AbsoluteExtendsNode(modulename)
        elif _token_ == "'loose_resolution'":
            self._scan("'loose_resolution'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.LooseResolutionNode()
        elif _token_ == "'allow_raw'":
            self._scan("'allow_raw'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.AllowRawNode()
        elif _token_ == "'allow_undeclared_globals'":
            self._scan("'allow_undeclared_globals'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.AllowUndeclaredGlobalsNode()
        elif _token_ == "'from'":
            self._scan("'from'")
            SPACE = self._scan('SPACE')
            modulename = self.modulename()
            SPACE = self._scan('SPACE')
            self._scan("'import'")
            SPACE = self._scan('SPACE')
            library_keyword = self.library_keyword()
            identifier = self.identifier()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.FromNode(modulename, identifier, library=library_keyword)
        elif _token_ == "'import'":
            self._scan("'import'")
            SPACE = self._scan('SPACE')
            library_keyword = self.library_keyword()
            modulename = self.modulename()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.ImportNode(modulename, library=library_keyword)
        elif _token_ == "'slurp'":
            self._scan("'slurp'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.CommentNode('slurp')
        elif _token_ == "'break'":
            self._scan("'break'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.BreakNode()
        elif _token_ == "'continue'":
            self._scan("'continue'")
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.ContinueNode()
        elif _token_ == "'global'":
            self._scan("'global'")
            SPACE = self._scan('SPACE')
            placeholder = self.placeholder()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.GlobalNode(placeholder.name)
        elif _token_ == "'attr'":
            self._scan("'attr'")
            SPACE = self._scan('SPACE')
            placeholder = self.placeholder()
            SPACE = self._scan('SPACE')
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            SPACE = self._scan('SPACE')
            literal = self.literal()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.AttributeNode(placeholder.name, literal)
        elif _token_ == "'filter'":
            self._scan("'filter'")
            SPACE = self._scan('SPACE')
            identifier = self.identifier()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.FilterAttributeNode('_filter_function', identifier)
        elif _token_ == "'do'":
            self._scan("'do'")
            SPACE = self._scan('SPACE')
            expression = self.expression()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.DoNode(expression)
        elif _token_ == "'set'":
            self._scan("'set'")
            SPACE = self._scan('SPACE')
            placeholder = self.placeholder()
            _lhs = ast.IdentifierNode(placeholder.name)
            _token_ = self._peek('SPACE', 'OPEN_BRACKET', 'ASSIGN_OPERATOR')
            if _token_ == 'OPEN_BRACKET':
                slice_node = self.slice_node(_lhs)
                _lhs = slice_node
            else:# in ['SPACE', 'ASSIGN_OPERATOR']
                pass
            if self._peek('SPACE', 'ASSIGN_OPERATOR') == 'SPACE':
                SPACE = self._scan('SPACE')
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            if self._peek('SPACE', '"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'") == 'SPACE':
                SPACE = self._scan('SPACE')
            expression = self.expression()
            _rhs = expression
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.AssignNode(_lhs, _rhs)
        else:# == "'echo'"
            self._scan("'echo'")
            SPACE = self._scan('SPACE')
            literal = self.literal()
            _true_exp = literal
            _test_exp, _false_exp = None, None
            if self._peek('SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'SPACE':
                SPACE = self._scan('SPACE')
                self._scan("'if'")
                SPACE = self._scan('SPACE')
                expression = self.expression()
                _test_exp = expression
                if self._peek('SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'SPACE':
                    SPACE = self._scan('SPACE')
                    self._scan("'else'")
                    SPACE = self._scan('SPACE')
                    literal = self.literal()
                    _false_exp = literal
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            return ast.EchoNode(_true_exp, _test_exp, _false_exp)

    def library_keyword(self):
        _library = False
        if self._peek("'library'", 'ID') == "'library'":
            self._scan("'library'")
            SPACE = self._scan('SPACE')
            _library = True
        return _library

    def modulename(self):
        identifier = self.identifier()
        _module_name_list = [identifier]
        while self._peek('DOT', 'SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'DOT':
            DOT = self._scan('DOT')
            identifier = self.identifier()
            _module_name_list.append(identifier)
        return _module_name_list

    def directive(self):
        START_DIRECTIVE = self._scan('START_DIRECTIVE')
        _token_ = self._peek('SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT', "'block'", "'i18n'", "'def'", "'for[ \\t]*'", "'strip_lines'", "'if'", "'implements'", "'extends'", "'absolute_extends'", "'loose_resolution'", "'allow_raw'", "'allow_undeclared_globals'", "'from'", "'import'", "'slurp'", "'break'", "'continue'", "'global'", "'attr'", "'filter'", "'do'", "'set'", "'echo'", 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'")
        if _token_ == 'SINGLE_LINE_COMMENT':
            SINGLE_LINE_COMMENT = self._scan('SINGLE_LINE_COMMENT')
            return ast.CommentNode(START_DIRECTIVE + SINGLE_LINE_COMMENT)
        elif _token_ == 'MULTI_LINE_COMMENT':
            MULTI_LINE_COMMENT = self._scan('MULTI_LINE_COMMENT')
            return ast.CommentNode(START_DIRECTIVE + MULTI_LINE_COMMENT)
        elif _token_ == "'block'":
            self._scan("'block'")
            SPACE = self._scan('SPACE')
            ID = self._scan('ID')
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            _block = ast.BlockNode(ID)
            start = CLOSE_DIRECTIVE.endswith('\n')
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', 'TEXT') != 'END_DIRECTIVE':
                block = self.block(start)
                _block.append(block)
            self.make_optional(_block.child_nodes, start)
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'block'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _block
        elif _token_ == "'i18n'":
            self._scan("'i18n'")
            _macro = ast.MacroNode('i18n')
            if self._peek('OPEN_PAREN', 'SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'OPEN_PAREN':
                OPEN_PAREN = self._scan('OPEN_PAREN')
                if self._peek('CLOSE_PAREN', 'START_PLACEHOLDER') == 'START_PLACEHOLDER':
                    macro_parameter_list = self.macro_parameter_list()
                    _macro.parameter_list = macro_parameter_list
                CLOSE_PAREN = self._scan('CLOSE_PAREN')
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            start = CLOSE_DIRECTIVE.endswith('\n')
            _macro.value = ''
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_BACKSLASH', 'TEXT', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE') != 'END_DIRECTIVE':
                i18n_body = self.i18n_body()
                _macro.value += i18n_body
                if self._peek('START_DIRECTIVE', 'LITERAL_DOLLAR_SIGN', 'LITERAL_BACKSLASH', 'TEXT', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE') == 'START_DIRECTIVE':
                    START_DIRECTIVE = self._scan('START_DIRECTIVE')
                    _macro.value += START_DIRECTIVE
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'i18n'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _macro
        elif _token_ == "'def'":
            self._scan("'def'")
            SPACE = self._scan('SPACE')
            ID = self._scan('ID')
            _def = ast.DefNode(ID)
            if self._peek('OPEN_PAREN', 'SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'OPEN_PAREN':
                OPEN_PAREN = self._scan('OPEN_PAREN')
                if self._peek('CLOSE_PAREN', 'START_PLACEHOLDER') == 'START_PLACEHOLDER':
                    parameter_list = self.parameter_list()
                    _def.parameter_list = parameter_list
                CLOSE_PAREN = self._scan('CLOSE_PAREN')
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            start = CLOSE_DIRECTIVE.endswith('\n')
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', 'TEXT') != 'END_DIRECTIVE':
                block = self.block(start)
                _def.append(block)
            self.make_optional(_def.child_nodes, start)
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'def'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _def
        elif _token_ == "'for[ \\t]*'":
            self._scan("'for[ \\t]*'")
            target_list = self.target_list()
            self._scan("'[ \\t]*in[ \\t]*'")
            expression_list = self.expression_list()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            _for_loop = ast.ForNode(target_list, expression_list)
            start = CLOSE_DIRECTIVE.endswith('\n')
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', 'TEXT') != 'END_DIRECTIVE':
                block = self.block(start)
                _for_loop.append(block)
            self.make_optional(_for_loop.child_nodes, start)
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'for'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _for_loop
        elif _token_ == "'strip_lines'":
            self._scan("'strip_lines'")
            self.strip_whitespace = True
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            _strip_lines_node = ast.StripLinesNode()
            start = CLOSE_DIRECTIVE.endswith('\n')
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT', 'END_DIRECTIVE') != 'END_DIRECTIVE':
                block = self.block(start)
                _strip_lines_node.append(block)
            self.make_optional(_strip_lines_node.child_nodes, start)
            self.strip_whitespace = False
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'strip_lines'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _strip_lines_node
        elif _token_ == "'if'":
            self._scan("'if'")
            SPACE = self._scan('SPACE')
            expression = self.expression()
            CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
            _if_node = ast.IfNode(expression)
            _last_condition_node = _if_node
            start = CLOSE_DIRECTIVE.endswith('\n')
            while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', "'#elif'", 'TEXT', "'#else'", 'END_DIRECTIVE') not in ["'#elif'", "'#else'", 'END_DIRECTIVE']:
                block = self.block(start)
                _if_node.append(block)
            self.make_optional(_if_node.child_nodes, start)
            while self._peek("'#elif'", "'#else'", 'END_DIRECTIVE') == "'#elif'":
                self._scan("'#elif'")
                SPACE = self._scan('SPACE')
                expression = self.expression()
                CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
                _elif_node = ast.IfNode(expression)
                _last_condition_node.else_.append(_elif_node)
                _last_condition_node = _elif_node
                start = CLOSE_DIRECTIVE.endswith('\n')
                while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT', "'#elif'", "'#else'", 'END_DIRECTIVE') not in ["'#elif'", "'#else'", 'END_DIRECTIVE']:
                    block = self.block(start)
                    _elif_node.append(block)
                self.make_optional(_elif_node.child_nodes, start)
            if self._peek("'#else'", 'END_DIRECTIVE') == "'#else'":
                self._scan("'#else'")
                CLOSE_DIRECTIVE = self.CLOSE_DIRECTIVE()
                start = CLOSE_DIRECTIVE.endswith('\n')
                while self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT', 'END_DIRECTIVE') != 'END_DIRECTIVE':
                    block = self.block(start)
                    _last_condition_node.else_.append(block)
                self.make_optional(_last_condition_node.else_.child_nodes, start)
            END_DIRECTIVE = self._scan('END_DIRECTIVE')
            SPACE = self._scan('SPACE')
            self._scan("'if'")
            CLOSE_END_DIRECTIVE = self.CLOSE_END_DIRECTIVE()
            return _if_node
        elif _token_ not in ['END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'"]:
            statement = self.statement()
            statement.statement = True
            return statement
        else:
            return ast.TextNode(START_DIRECTIVE)

    def block(self, start=False):
        _token_ = self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT')
        if _token_ == 'LITERAL_DOLLAR_SIGN':
            LITERAL_DOLLAR_SIGN = self._scan('LITERAL_DOLLAR_SIGN')
            return ast.TextNode('$')
        elif _token_ == 'LITERAL_HASH':
            LITERAL_HASH = self._scan('LITERAL_HASH')
            return ast.TextNode('#')
        elif _token_ == 'LITERAL_BACKSLASH':
            LITERAL_BACKSLASH = self._scan('LITERAL_BACKSLASH')
            return ast.TextNode('\\')
        elif _token_ == 'START_DIRECTIVE':
            directive = self.directive()
            return directive
        elif _token_ == 'TEXT':
            text = self.text()
            return text
        elif _token_ == 'SPACE':
            SPACE = self._scan('SPACE')
            _node_list = ast.NodeList()
            _node_list.append(ast.WhitespaceNode(SPACE))
            if self._peek('START_DIRECTIVE', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") == 'START_DIRECTIVE':
                directive = self.directive()
                if start: _node_list[-1] = ast.OptionalWhitespaceNode(SPACE)
                _node_list.append(directive)
            return _node_list
        elif _token_ == 'NEWLINE':
            NEWLINE = self._scan('NEWLINE')
            _node_list = ast.NodeList()
            _node_list.append(ast.NewlineNode(NEWLINE))
            if self._peek('SPACE', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") == 'SPACE':
                SPACE = self._scan('SPACE')
                _node_list.append(ast.WhitespaceNode(SPACE))
                if self._peek('START_DIRECTIVE', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") == 'START_DIRECTIVE':
                    directive = self.directive()
                    _node_list[-1] = ast.OptionalWhitespaceNode(SPACE)
                    _node_list.append(directive)
            return _node_list
        else:# == 'START_PLACEHOLDER'
            _parameter_list = None
            START_PLACEHOLDER = self._scan('START_PLACEHOLDER')
            _primary = ast.TextNode(START_PLACEHOLDER)
            if self._peek('PLACEHOLDER_OPEN_BRACE', 'ID', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") in ['PLACEHOLDER_OPEN_BRACE', 'ID']:
                _token_ = self._peek('PLACEHOLDER_OPEN_BRACE', 'ID')
                if _token_ == 'PLACEHOLDER_OPEN_BRACE':
                    PLACEHOLDER_OPEN_BRACE = self._scan('PLACEHOLDER_OPEN_BRACE')
                    placeholder_in_text = self.placeholder_in_text()
                    _primary = placeholder_in_text
                    if self._peek('PIPE', 'PLACEHOLDER_CLOSE_BRACE') == 'PIPE':
                        PIPE = self._scan('PIPE')
                        placeholder_parameter_list = self.placeholder_parameter_list()
                        _parameter_list = placeholder_parameter_list
                    PLACEHOLDER_CLOSE_BRACE = self._scan('PLACEHOLDER_CLOSE_BRACE')
                else:# == 'ID'
                    placeholder_in_text = self.placeholder_in_text()
                    _primary = placeholder_in_text
            if type(_primary) != ast.TextNode: return ast.PlaceholderSubstitutionNode(_primary, _parameter_list)
            return _primary

    def text_or_placeholders(self, start=False):
        _token_ = self._peek('LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT')
        if _token_ == 'LITERAL_DOLLAR_SIGN':
            LITERAL_DOLLAR_SIGN = self._scan('LITERAL_DOLLAR_SIGN')
            return ast.TextNode('$')
        elif _token_ == 'LITERAL_HASH':
            LITERAL_HASH = self._scan('LITERAL_HASH')
            return ast.TextNode('#')
        elif _token_ == 'LITERAL_BACKSLASH':
            LITERAL_BACKSLASH = self._scan('LITERAL_BACKSLASH')
            return ast.TextNode('\\')
        elif _token_ == 'START_DIRECTIVE':
            START_DIRECTIVE = self._scan('START_DIRECTIVE')
            return ast.TextNode(START_DIRECTIVE)
        elif _token_ == 'TEXT':
            text = self.text()
            return text
        elif _token_ == 'SPACE':
            SPACE = self._scan('SPACE')
            return ast.WhitespaceNode(SPACE)
        elif _token_ == 'NEWLINE':
            NEWLINE = self._scan('NEWLINE')
            _node_list = ast.NodeList()
            _node_list.append(ast.NewlineNode(NEWLINE))
            if self._peek('SPACE', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT') == 'SPACE':
                SPACE = self._scan('SPACE')
                _node_list.append(ast.WhitespaceNode(SPACE))
            return _node_list
        else:# == 'START_PLACEHOLDER'
            _parameter_list = None
            START_PLACEHOLDER = self._scan('START_PLACEHOLDER')
            _primary = ast.TextNode(START_PLACEHOLDER)
            if self._peek('PLACEHOLDER_OPEN_BRACE', 'ID', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'TEXT') in ['PLACEHOLDER_OPEN_BRACE', 'ID']:
                _token_ = self._peek('PLACEHOLDER_OPEN_BRACE', 'ID')
                if _token_ == 'PLACEHOLDER_OPEN_BRACE':
                    PLACEHOLDER_OPEN_BRACE = self._scan('PLACEHOLDER_OPEN_BRACE')
                    placeholder_in_text = self.placeholder_in_text()
                    _primary = placeholder_in_text
                    if self._peek('PIPE', 'PLACEHOLDER_CLOSE_BRACE') == 'PIPE':
                        PIPE = self._scan('PIPE')
                        placeholder_parameter_list = self.placeholder_parameter_list()
                        _parameter_list = placeholder_parameter_list
                    PLACEHOLDER_CLOSE_BRACE = self._scan('PLACEHOLDER_CLOSE_BRACE')
                else:# == 'ID'
                    placeholder_in_text = self.placeholder_in_text()
                    _primary = placeholder_in_text
            if type(_primary) == ast.TextNode: return _primary
            _placeholder_sub = ast.PlaceholderSubstitutionNode(_primary, _parameter_list)
            return _placeholder_sub

    def text(self):
        TEXT = self._scan('TEXT')
        return ast.TextNode(TEXT)

    def placeholder_in_text(self):
        ID = self._scan('ID')
        _primary = ast.PlaceholderNode(ID)
        while self._peek('DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET', 'PIPE', 'PLACEHOLDER_CLOSE_BRACE', 'END', 'LITERAL_DOLLAR_SIGN', 'LITERAL_HASH', 'LITERAL_BACKSLASH', 'START_DIRECTIVE', 'SPACE', 'NEWLINE', 'START_PLACEHOLDER', 'END_DIRECTIVE', "'#elif'", 'TEXT', "'#else'") in ['DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET']:
            placeholder_suffix_expression = self.placeholder_suffix_expression(_primary)
            _primary = placeholder_suffix_expression
        return _primary

    def placeholder_suffix_expression(self, _previous_primary):
        _token_ = self._peek('DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET')
        if _token_ == 'DOT':
            DOT = self._scan('DOT')
            ID = self._scan('ID')
            _primary = ast.GetUDNNode(_previous_primary, ID)
        elif _token_ == 'PLACEHOLDER_OPEN_PAREN':
            PLACEHOLDER_OPEN_PAREN = self._scan('PLACEHOLDER_OPEN_PAREN')
            _arg_list = None
            if self._peek('CLOSE_PAREN', '"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'") != 'CLOSE_PAREN':
                argument_list = self.argument_list()
                _arg_list = argument_list
            CLOSE_PAREN = self._scan('CLOSE_PAREN')
            _primary = ast.CallFunctionNode(_previous_primary, _arg_list)
        else:# == 'OPEN_BRACKET'
            slice_node = self.slice_node(_previous_primary)
            _primary = slice_node
        return _primary

    def placeholder(self):
        START_PLACEHOLDER = self._scan('START_PLACEHOLDER')
        _token_ = self._peek('ID')
        if _token_ == 'ID': return ast.PlaceholderNode(self._scan('ID'))
        return ast.TextNode(START_PLACEHOLDER)

    def target_list(self):
        _target_list = ast.TargetListNode()
        target = self.target()
        _target_list.append(target)
        while self._peek('COMMA_DELIMITER', "'[ \\t]*in[ \\t]*'", 'CLOSE_PAREN', 'CLOSE_BRACKET') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            target = self.target()
            _target_list.append(target)
        return _target_list

    def expression_list(self):
        _expression_list = ast.ExpressionListNode()
        expression = self.expression()
        _expression_list.append(expression)
        while self._peek('COMMA_DELIMITER', 'SPACE', 'CLOSE_DIRECTIVE_TOKEN') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            expression = self.expression()
            _expression_list.append(expression)
        return _expression_list

    def target(self):
        _token_ = self._peek('START_PLACEHOLDER', 'OPEN_PAREN', 'OPEN_BRACKET')
        if _token_ == 'START_PLACEHOLDER':
            placeholder = self.placeholder()
            return ast.TargetNode(placeholder.name)
        elif _token_ == 'OPEN_PAREN':
            OPEN_PAREN = self._scan('OPEN_PAREN')
            target_list = self.target_list()
            CLOSE_PAREN = self._scan('CLOSE_PAREN')
            return target_list
        else:# == 'OPEN_BRACKET'
            OPEN_BRACKET = self._scan('OPEN_BRACKET')
            target_list = self.target_list()
            CLOSE_BRACKET = self._scan('CLOSE_BRACKET')
            return target_list

    def parameter(self):
        placeholder = self.placeholder()
        _node = ast.ParameterNode(placeholder.name)
        if self._peek('ASSIGN_OPERATOR', 'COMMA_DELIMITER', 'CLOSE_PAREN') == 'ASSIGN_OPERATOR':
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            expression = self.expression()
            _node.default = expression
        return _node

    def parameter_list(self):
        _parameter_list = ast.ParameterListNode()
        parameter = self.parameter()
        _parameter_list.append(parameter)
        while self._peek('COMMA_DELIMITER', 'CLOSE_PAREN') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            parameter = self.parameter()
            _parameter_list.append(parameter)
        return _parameter_list

    def macro_parameter(self):
        placeholder = self.placeholder()
        _node = ast.ParameterNode(placeholder.name)
        if self._peek('ASSIGN_OPERATOR', 'COMMA_DELIMITER', 'CLOSE_PAREN') == 'ASSIGN_OPERATOR':
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            literal = self.literal()
            _node.default = literal
        return _node

    def macro_parameter_list(self):
        _parameter_list = ast.ParameterListNode()
        macro_parameter = self.macro_parameter()
        _parameter_list.append(macro_parameter)
        while self._peek('COMMA_DELIMITER', 'CLOSE_PAREN') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            macro_parameter = self.macro_parameter()
            _parameter_list.append(macro_parameter)
        return _parameter_list

    def literal_or_identifier(self):
        _token_ = self._peek('"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'ID')
        if _token_ != 'ID':
            literal = self.literal()
            return literal
        else:# == 'ID'
            identifier = self.identifier()
            return identifier

    def placeholder_parameter(self):
        identifier = self.identifier()
        _node = ast.ParameterNode(identifier.name)
        if self._peek('ASSIGN_OPERATOR', 'COMMA_DELIMITER', 'PLACEHOLDER_CLOSE_BRACE') == 'ASSIGN_OPERATOR':
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            literal_or_identifier = self.literal_or_identifier()
            _node.default = literal_or_identifier
        return _node

    def placeholder_parameter_list(self):
        _parameter_list = ast.ParameterListNode()
        placeholder_parameter = self.placeholder_parameter()
        _parameter_list.append(placeholder_parameter)
        while self._peek('COMMA_DELIMITER', 'PLACEHOLDER_CLOSE_BRACE') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            placeholder_parameter = self.placeholder_parameter()
            _parameter_list.append(placeholder_parameter)
        return _parameter_list

    def stringliteral(self):
        _token_ = self._peek('\'"\'', '"\'"')
        if _token_ == '\'"\'':
            self._scan('\'"\'')
            DOUBLE_QUOTE_STR = self._scan('DOUBLE_QUOTE_STR')
            self._scan('\'"\'')
            return unicode(eval('"%s"' % DOUBLE_QUOTE_STR))
        else:# == '"\'"'
            self._scan('"\'"')
            SINGLE_QUOTE_STR = self._scan('SINGLE_QUOTE_STR')
            self._scan('"\'"')
            return unicode(eval("'%s'" % SINGLE_QUOTE_STR))

    def literal(self):
        _token_ = self._peek('"True"', '"False"', '\'"\'', '"\'"', 'NUM')
        if _token_ == '"True"':
            self._scan('"True"')
            return ast.LiteralNode(True)
        elif _token_ == '"False"':
            self._scan('"False"')
            return ast.LiteralNode(False)
        elif _token_ != 'NUM':
            stringliteral = self.stringliteral()
            return ast.LiteralNode(stringliteral)
        else:# == 'NUM'
            NUM = self._scan('NUM')
            int_part = NUM
            if self._peek('"\\."', 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET', 'COMMA_DELIMITER', "'[ \\t]*\\*[ \\t]*'", 'CLOSE_PAREN', "'[ \\t]*\\/[ \\t]*'", "'[ \\t]*\\%[ \\t]*'", 'PLACEHOLDER_CLOSE_BRACE', "'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'END', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_BRACE') == '"\\."':
                self._scan('"\\."')
                NUM = self._scan('NUM')
                return ast.LiteralNode(float('%s.%s' % (int_part, NUM)))
            return ast.LiteralNode(int(int_part))

    def identifier(self):
        ID = self._scan('ID')
        return ast.IdentifierNode(ID)

    def primary(self, in_placeholder_context=False):
        _token_ = self._peek('START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE')
        if _token_ == 'START_PLACEHOLDER':
            placeholder = self.placeholder()
            _primary = placeholder
        elif _token_ == 'ID':
            identifier = self.identifier()
            _primary = identifier
            if in_placeholder_context: _primary = ast.PlaceholderNode(_primary.name)
        elif _token_ not in ['OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE']:
            literal = self.literal()
            _primary = literal
        elif _token_ == 'OPEN_BRACKET':
            OPEN_BRACKET = self._scan('OPEN_BRACKET')
            _list_literal = ast.ListLiteralNode()
            if self._peek('COMMA_DELIMITER', 'CLOSE_BRACKET', '"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'") not in ['COMMA_DELIMITER', 'CLOSE_BRACKET']:
                expression = self.expression()
                _list_literal.append(expression)
                while self._peek('COMMA_DELIMITER', 'CLOSE_BRACKET') == 'COMMA_DELIMITER':
                    COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
                    expression = self.expression()
                    _list_literal.append(expression)
            CLOSE_BRACKET = self._scan('CLOSE_BRACKET')
            _primary = _list_literal
        elif _token_ == 'OPEN_PAREN':
            OPEN_PAREN = self._scan('OPEN_PAREN')
            _tuple_literal = ast.TupleLiteralNode()
            if self._peek('COMMA_DELIMITER', 'CLOSE_PAREN', '"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'") not in ['COMMA_DELIMITER', 'CLOSE_PAREN']:
                expression = self.expression()
                _tuple_literal.append(expression)
                while self._peek('COMMA_DELIMITER', 'CLOSE_PAREN') == 'COMMA_DELIMITER':
                    COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
                    expression = self.expression()
                    _tuple_literal.append(expression)
            CLOSE_PAREN = self._scan('CLOSE_PAREN')
            _primary = _tuple_literal
        else:# == 'OPEN_BRACE'
            OPEN_BRACE = self._scan('OPEN_BRACE')
            _dict_literal = ast.DictLiteralNode()
            if self._peek('COMMA_DELIMITER', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE', '"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'") not in ['COMMA_DELIMITER', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE']:
                expression = self.expression()
                _key = expression
                COLON_DELIMITER = self._scan('COLON_DELIMITER')
                expression = self.expression()
                _dict_literal.append((_key, expression))
                while self._peek('COMMA_DELIMITER', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == 'COMMA_DELIMITER':
                    COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
                    expression = self.expression()
                    _key = expression
                    COLON_DELIMITER = self._scan('COLON_DELIMITER')
                    expression = self.expression()
                    _dict_literal.append((_key, expression))
            _token_ = self._peek('CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE')
            if _token_ == 'CLOSE_BRACE':
                CLOSE_BRACE = self._scan('CLOSE_BRACE')
            else:# == 'PLACEHOLDER_CLOSE_BRACE'
                PLACEHOLDER_CLOSE_BRACE = self._scan('PLACEHOLDER_CLOSE_BRACE')
            _primary = _dict_literal
        while self._peek('DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET', "'[ \\t]*\\*[ \\t]*'", "'[ \\t]*\\/[ \\t]*'", "'[ \\t]*\\%[ \\t]*'", "'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') in ['DOT', 'PLACEHOLDER_OPEN_PAREN', 'OPEN_BRACKET']:
            placeholder_suffix_expression = self.placeholder_suffix_expression(_primary)
            _primary = placeholder_suffix_expression
        return _primary

    def define_list(self):
        argument_list = self.argument_list()
        END = self._scan('END')
        return argument_list

    def rhs_expression(self):
        expression = self.expression()
        END = self._scan('END')
        return expression

    def argument_list(self):
        _pargs, _kargs = [], []
        expression = self.expression()
        _arg = expression
        while self._peek('COMMA_DELIMITER', 'ASSIGN_OPERATOR', 'END', 'CLOSE_PAREN') == 'COMMA_DELIMITER':
            COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
            _pargs.append(_arg)
            expression = self.expression()
            _arg = expression
        if self._peek('ASSIGN_OPERATOR', 'COMMA_DELIMITER', 'END', 'CLOSE_PAREN') == 'ASSIGN_OPERATOR':
            ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
            if not isinstance(_arg, (ast.IdentifierNode)): raise SyntaxError(self._scanner.pos, "keyword arg can't be complex expression: %s" % _arg)
            _karg = ast.ParameterNode(_arg.name)
            _arg = None
            expression = self.expression()
            _karg.default = expression
            _kargs.append(_karg)
            while self._peek('COMMA_DELIMITER', 'END', 'CLOSE_PAREN') == 'COMMA_DELIMITER':
                COMMA_DELIMITER = self._scan('COMMA_DELIMITER')
                identifier = self.identifier()
                _karg = ast.ParameterNode(identifier.name)
                ASSIGN_OPERATOR = self._scan('ASSIGN_OPERATOR')
                expression = self.expression()
                _karg.default = expression
                _kargs.append(_karg)
        if _arg: _pargs.append(_arg)
        return ast.ArgListNode(_pargs, _kargs)

    def expression(self):
        or_test = self.or_test()
        return or_test

    def or_test(self):
        and_test = self.and_test()
        _test = and_test
        while self._peek("'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*or[ \\t]*'":
            self._scan("'[ \\t]*or[ \\t]*'")
            and_test = self.and_test()
            _test = ast.BinOpExpressionNode('or', _test, and_test)
        return _test

    def and_test(self):
        not_test = self.not_test()
        _test = not_test
        while self._peek("'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*and[ \\t]*'":
            self._scan("'[ \\t]*and[ \\t]*'")
            not_test = self.not_test()
            _test = ast.BinOpExpressionNode('and', _test, not_test)
        return _test

    def not_test(self):
        _token_ = self._peek('"[ \\t]*not[ \\t]*"', 'START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'")
        if _token_ != '"[ \\t]*not[ \\t]*"':
            comparison = self.comparison()
            return comparison
        else:# == '"[ \\t]*not[ \\t]*"'
            self._scan('"[ \\t]*not[ \\t]*"')
            not_test = self.not_test()
            return ast.UnaryOpNode('not', not_test)

    def u_expr(self):
        _token_ = self._peek('START_PLACEHOLDER', 'ID', '"True"', '"False"', '\'"\'', '"\'"', 'NUM', 'OPEN_BRACKET', 'OPEN_PAREN', 'OPEN_BRACE', "'[ \\t]*\\-[ \\t]*'")
        if _token_ != "'[ \\t]*\\-[ \\t]*'":
            primary = self.primary()
            return primary
        else:# == "'[ \\t]*\\-[ \\t]*'"
            self._scan("'[ \\t]*\\-[ \\t]*'")
            u_expr = self.u_expr()
            return ast.UnaryOpNode('-', u_expr)

    def m_expr(self):
        u_expr = self.u_expr()
        _expr = u_expr
        while self._peek("'[ \\t]*\\*[ \\t]*'", "'[ \\t]*\\/[ \\t]*'", "'[ \\t]*\\%[ \\t]*'", "'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*\\*[ \\t]*'":
            self._scan("'[ \\t]*\\*[ \\t]*'")
            u_expr = self.u_expr()
            _expr = ast.BinOpExpressionNode('*', _expr, u_expr)
        while self._peek("'[ \\t]*\\/[ \\t]*'", "'[ \\t]*\\%[ \\t]*'", "'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*\\/[ \\t]*'":
            self._scan("'[ \\t]*\\/[ \\t]*'")
            u_expr = self.u_expr()
            _expr = ast.BinOpExpressionNode('/', _expr, u_expr)
        while self._peek("'[ \\t]*\\%[ \\t]*'", "'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*\\%[ \\t]*'":
            self._scan("'[ \\t]*\\%[ \\t]*'")
            u_expr = self.u_expr()
            _expr = ast.BinOpExpressionNode('%', _expr, u_expr)
        return _expr

    def a_expr(self):
        m_expr = self.m_expr()
        _expr = m_expr
        while self._peek("'[ \\t]*\\+[ \\t]*'", "'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*\\+[ \\t]*'":
            self._scan("'[ \\t]*\\+[ \\t]*'")
            m_expr = self.m_expr()
            _expr = ast.BinOpExpressionNode('+', _expr, m_expr)
        while self._peek("'[ \\t]*\\-[ \\t]*'", 'COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == "'[ \\t]*\\-[ \\t]*'":
            self._scan("'[ \\t]*\\-[ \\t]*'")
            m_expr = self.m_expr()
            _expr = ast.BinOpExpressionNode('-', _expr, m_expr)
        return _expr

    def comparison(self):
        a_expr = self.a_expr()
        _left_side = a_expr
        while self._peek('COMP_OPERATOR', "'[ \\t]*and[ \\t]*'", "'[ \\t]*or[ \\t]*'", 'SPACE', 'CLOSE_DIRECTIVE_TOKEN', 'END', 'COMMA_DELIMITER', 'COLON_DELIMITER', 'ASSIGN_OPERATOR', 'CLOSE_BRACKET', 'CLOSE_PAREN', 'CLOSE_BRACE', 'PLACEHOLDER_CLOSE_BRACE') == 'COMP_OPERATOR':
            COMP_OPERATOR = self._scan('COMP_OPERATOR')
            a_expr = self.a_expr()
            _left_side = ast.BinOpExpressionNode(COMP_OPERATOR.strip(), _left_side, a_expr)
        return _left_side

    def slice_node(self, _expression):
        OPEN_BRACKET = self._scan('OPEN_BRACKET')
        expression = self.expression()
        _node = ast.SliceNode(_expression, expression)
        CLOSE_BRACKET = self._scan('CLOSE_BRACKET')
        return _node


def parse(rule, text):
    P = _SpitfireParser(_SpitfireParserScanner(text))
    return wrap_error_reporter(P, rule)




@ast.track_line_numbers(exempt_methods="make_optional")
class SpitfireParser(_SpitfireParser):
  strip_whitespace = False

  def make_optional(self, node_list, starts_new_line=False):
    if self.strip_whitespace:
      return ast.strip_whitespace(node_list, starts_new_line=starts_new_line)
    else:
      return ast.make_optional(node_list)
