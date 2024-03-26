import json

class LexicalAnalyzer:
    def __init__(self):
        self.php_elements = {
            'operations': {
                1: '+', 2: '-', 3: '*', 4: '/', 5: '%', 6: '**', 7: '.', 8: '++', 9: '--',
                10: '+=', 11: '-=', 12: '*=', 13: '/=', 14: '%=', 15: '**=', 16: '.=',
                17: '==', 18: '!=', 19: '>', 20: '<', 21: '>=', 22: '<=', 23: '&&', 24: '||',
                25: '!', 26: '&', 27: '|', 28: '^', 29: '~', 30: '<<', 31: '>>', 32: '<=>',
                33: '?:', 34: '??', 35: 'and', 36: 'xor', 37: 'or'
            },
            'delimiters': {
                1: ' ', 2: '(', 3: ')', 4: ',', 5: '"', 6: "'", 7: '[', 8: ']', 9: '{',
                10: '}', 11: ';', 12: ':', 13: '.', 14: '/', 15: '\\', 16: '\n'
            },
            'keywords': {
                1: 'if', 2: 'else', 3: 'elseif', 4: 'endif', 5: 'switch', 6: 'case',
                7: 'default', 8: 'break', 9: 'continue', 10: 'while', 11: 'do', 12: 'for',
                13: 'foreach', 14: 'as', 15: 'return', 16: 'include', 17: 'include_once',
                18: 'require', 19: 'require_once', 20: 'echo', 21: 'print', 22: 'isset',
                23: 'unset', 24: 'empty', 25: 'die', 26: 'exit', 27: 'function',
                28: 'global', 29: 'static', 30: 'var', 31: 'const', 32: 'declare', 33: 'list'
            },
            'constants': {
                1: 'null',
                2: 'true',
                3: 'false'
            }
        }

    def check(self, tokens, token_class, token_value):
        if token_value not in tokens[token_class]:
            token_code = str(len(tokens[token_class]) + 1)
            tokens[token_class][token_value] = token_class + token_code

    def get_operation(self, input_sequence, i):
        for k in range(3, 0, -1):
            if i + k <= len(input_sequence):
                buffer = input_sequence[i:i + k]
                if buffer in self.php_elements['operations'].values():
                    return buffer
        return ''

    def get_separator(self, input_sequence, i):
        buffer = input_sequence[i]
        if buffer in self.php_elements['delimiters'].values():
            return buffer
        return ''

    def analyze_php(self, input_sequence):
        tokens = {'W': {}, 'I': {}, 'O': {}, 'R': {}, 'N': {}, 'C': {}}

        for keyword in self.php_elements['keywords'].values():
            self.check(tokens, 'W', keyword)
        for operation in self.php_elements['operations'].values():
            self.check(tokens, 'O', operation)
        for delimiter in self.php_elements['delimiters'].values():
            self.check(tokens, 'R', delimiter)
        for constant in self.php_elements['constants'].values():
            self.check(tokens, 'C', constant)

        i = 0
        state = 'S'
        output_sequence = buffer = ''

        while i < len(input_sequence):
            symbol = input_sequence[i]
            operation = self.get_operation(input_sequence, i)
            separator = self.get_separator(input_sequence, i)

            if state == 'S':
                buffer = ''
                if symbol.isalpha() or symbol == '_':
                    state = 'q1'
                    buffer += symbol
                elif symbol.isdigit():
                    state = 'q3'
                    buffer += symbol
                elif symbol == "'":
                    state = 'q9'
                    buffer += symbol
                elif symbol == '"':
                    state = 'q10'
                    buffer += symbol
                elif symbol == '/':
                    state = 'q11'
                elif operation:
                    self.check(tokens, 'O', operation)
                    output_sequence += tokens['O'][operation] + ' '
                    i += len(operation) - 1
                elif separator:
                    if separator != ' ':
                        self.check(tokens, 'R', separator)
                        output_sequence += tokens['R'][separator]
                        if separator == '\n':
                            output_sequence += '\n'
                        else:
                            output_sequence += ' '
                elif i == len(input_sequence) - 1:
                    state = 'Z'
            elif state == 'q1':
                if symbol.isalnum() or symbol == '_':
                    buffer += symbol
                else:
                    if operation or separator:
                        if buffer in self.php_elements['keywords'].values():
                            output_sequence += tokens['W'][buffer] + ' '
                        elif buffer in self.php_elements['constants'].values():
                            output_sequence += tokens['C'][buffer] + ' '
                        else:
                            self.check(tokens, 'I', buffer)
                            output_sequence += tokens['I'][buffer] + ' '
                        if operation:
                            self.check(tokens, 'O', operation)
                            output_sequence += tokens['O'][operation] + ' '
                            i += len(operation) - 1
                        if separator:
                            if separator != ' ':
                                self.check(tokens, 'R', separator)
                                output_sequence += tokens['R'][separator]
                                if separator == '\n':
                                    output_sequence += '\n'
                                else:
                                    output_sequence += ' '
                    state = 'S'
            elif state == 'q3':
                if symbol.isdigit():
                    buffer += symbol
                elif symbol == '.':
                    state = 'q4'
                    buffer += symbol
                elif symbol == 'e' or symbol == 'E':
                    state = 'q6'
                    buffer += symbol
                else:
                    if operation or separator:
                        self.check(tokens, 'N', buffer)
                        output_sequence += tokens['N'][buffer] + ' '
                        if operation:
                            self.check(tokens, 'O', operation)
                            output_sequence += tokens['O'][operation] + ' '
                            i += len(operation) - 1
                        if separator:
                            if separator != ' ':
                                self.check(tokens, 'R', separator)
                                output_sequence += tokens['R'][separator]
                                if separator == '\n':
                                    output_sequence += '\n'
                                else:
                                    output_sequence += ' '
                        state = 'S'
            elif state == 'q4':
                if symbol.isdigit():
                    state = 'q5'
                    buffer += symbol
            elif state == 'q5':
                if symbol.isdigit():
                    buffer += symbol
                elif symbol == 'e' or symbol == 'E':
                    state = 'q6'
                    buffer += symbol
                else:
                    if operation or separator:
                        self.check(tokens, 'N', buffer)
                        output_sequence += tokens['N'][buffer] + ' '
                        if operation:
                            self.check(tokens, 'O', operation)
                            output_sequence += tokens['O'][operation] + ' '
                            i += len(operation) - 1
                        if separator:
                            if separator != ' ':
                                self.check(tokens, 'R', separator)
                                output_sequence += tokens['R'][separator]
                                if separator == '\n':
                                    output_sequence += '\n'
                                else:
                                    output_sequence += ' '
                        state = 'S'
            elif state == 'q6':
                if symbol == '-' or symbol == '+':
                    state = 'q7'
                    buffer += symbol
                elif symbol.isdigit():
                    state = 'q8'
                    buffer += symbol
            elif state == 'q7':
                if symbol.isdigit():
                    state = 'q8'
                    buffer += symbol
            elif state == 'q8':
                if symbol.isdigit():
                    buffer += symbol
                else:
                    if operation or separator:
                        self.check(tokens, 'N', buffer)
                        output_sequence += tokens['N'][buffer] + ' '
                        if operation:
                            self.check(tokens, 'O', operation)
                            output_sequence += tokens['O'][operation] + ' '
                            i += len(operation) - 1
                        if separator:
                            if separator != ' ':
                                self.check(tokens, 'R', separator)
                                output_sequence += tokens['R'][separator]
                                if separator == '\n':
                                    output_sequence += '\n'
                                else:
                                    output_sequence += ' '
                    state = 'S'
            elif state == 'q9':
                if symbol != "'":
                    buffer += symbol
                elif symbol == "'":
                    buffer += symbol
                    self.check(tokens, 'C', buffer)
                    output_sequence += tokens['C'][buffer] + ' '
                    state = 'S'
            elif state == 'q10':
                if symbol != '"':
                    buffer += symbol
                elif symbol == '"':
                    buffer += symbol
                    self.check(tokens, 'C', buffer)
                    output_sequence += tokens['C'][buffer] + ' '
                    state = 'S'
            elif state == 'q11':
                if symbol == '/':
                    state = 'q12'
                elif symbol == '*':
                    state = 'q13'
                else:
                    self.check(tokens, 'O', '/')
                    output_sequence += tokens['O']['/'] + ' '
                    state = 'S'
                    i -= 1
            elif state == 'q12':
                if symbol == '\n':
                    state = 'S'
                elif i == len(input_sequence) - 1:
                    state = 'Z'
            elif state == 'q13':
                if symbol == '*':
                    state = 'q14'
                elif i == len(input_sequence) - 1:
                    state = 'Z'
            elif state == 'q14':
                if symbol == '/':
                    state = 'S'
                elif symbol == '*':
                    pass
                else:
                    state = 'q13'
            i += 1

        return output_sequence, tokens


    def analyze_file(self, file_path):
        with open(file_path, 'r') as file:
            php_code = file.read()

        output_sequence, tokens = self.analyze_php(php_code)

        with open('tokens.txt', 'w') as file:
            file.write(output_sequence)

        for token_class in tokens.keys():
            with open(f'../out/{token_class}.json', 'w') as file:
                data = {val: key for key, val in tokens[token_class].items()}
                json.dump(data, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    analyzer = LexicalAnalyzer()
    analyzer.analyze_file('php_code.txt')