#!/usr/bin/env python3

import tree_sitter_apertium as TSA
import argparse
import re

class Replacer:
    grammar = None
    def __init__(self, inbytes, replacements):
        self.in_data = inbytes
        self.tree = TSA.parse_bytes(self.in_data, self.grammar)
        self.out_data = ''
        self.idx = 0
        self.replacements = replacements
    def single_replace(self, instr):
        return instr
    def iter_ranges(self):
        pass
    def do_replace(self):
        for start, end in self.iter_ranges():
            if start > self.idx:
                self.out_data += self.in_data[self.idx:start].decode('utf-8')
            txt = self.in_data[start:end].decode('utf-8')
            self.out_data += self.single_replace(txt)
            self.idx = end
        if self.idx < len(self.in_data):
            self.out_data += self.in_data[self.idx:].decode('utf-8')

def replace_list(ls, src, trg, comp=lambda x, y: x == y):
    ret = []
    i = 0
    while i + len(src) <= len(ls):
        if all(comp(a, b) for a, b in zip(ls[i:], src)):
            ret += trg
            i += len(src)
        else:
            ret.append(ls[i])
            i += 1
    ret += ls[i:]
    return ret
            
class LexdReplacer(Replacer):
    grammar = TSA.LEXD
    lexicon_tokenizer = re.compile(r'<(?:[^>\\]|\.)*>|\{(?:[^\}\\]|\.)*\}|\\.|[^\\]')
    def iter_ranges(self):
        qr = TSA.LEXD.query('(lexicon_segment) @seg')
        for node, _ in qr.captures(self.tree):
            loc = node.start_byte
            for c in node.children:
                if c.type in ['tag_setting', 'regex', 'colon']:
                    if loc != c.start_byte:
                        yield loc, c.start_byte
                        loc = c.end_byte
            if loc < node.end_byte:
                yield loc, node.end_byte
    def single_replace(self, instr):
        segments = self.lexicon_tokenizer.findall(instr)
        for src, trg in self.replacements:
            segments = replace_list(segments, src, trg)
        return ''.join(segments)

class TwolReplacer(Replacer):
    grammar = TSA.TWOLC
    def iter_ranges(self):
        qr = TSA.TWOLC.query('(symbol) @sym')
        for node, _ in qr.captures(self.tree):
            yield node.start_byte, node.end_byte
    def single_replace(self, instr):
        for src, trg in self.replacements:
            if len(src) == len(trg) == 1 and instr == src[0]:
                instr = trg[0]
        return instr

class XfstReplacer(Replacer):
    grammar = TSA.XFST
    def iter_ranges(self):
        qr = TSA.XFST.query('(symbol) @sym')
        for node, _ in qr.captures(self.tree):
            yield node.start_byte, node.end_byte
    def single_replace(self, instr):
        for src, trg in self.replacements:
            if len(src) == len(trg) == 1 and instr == src[0]:
                instr = trg[0]
        return instr

class LexcReplacer(Replacer):
    grammar = TSA.LEXC
    lexicon_tokenizer = re.compile(r'%<(?:[^>%]|%.)*%>|%\{(?:[^\}%]|%.)*%\}|%.|[^%]')
    def iter_ranges(self):
        qr = TSA.TWOLC.query('(lexicon_string) @sym')
        for node, _ in qr.captures(self.tree):
            yield node.start_byte, node.end_byte
    def single_replace(self, instr):
        segments = self.lexicon_tokenizer.findall(instr)
        for src, trg in self.replacements:
            segments = replace_list(segments, src, trg)
        return ''.join(segments)

def tokenize_replacement(arg):
    return [a.split() for a in arg.split('/')]

def replace_file(fin, fout, repl, typ):
    replacers = {
        'lexd': LexdReplacer,
        'twol': TwolReplacer,
        'lexc': LexcReplacer,
        'xfst': XfstReplacer,
    }
    r = replacers[typ](fin.read(), [tokenize_replacement(r) for r in repl])
    r.do_replace()
    fout.write(r.out_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Search and replace for Apertium source files')
    parser.add_argument('infile', type=argparse.FileType('rb'),
                        help='Input file (- for stdin)')
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help='Output file (- for stdout), must be different from input file')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', '--find', type=str, action='append')
    mode.add_argument('-r', '--replace', type=str, action='append')
    lang = parser.add_mutually_exclusive_group(required=True)
    lang.add_argument('-d', '--lexd', action='store_const', dest='lang',
                      const='lexd', help='Input is a lexd file')
    lang.add_argument('-c', '--lexc', action='store_const', dest='lang',
                      const='lexc', help='Input is a LexC file')
    lang.add_argument('-t', '--twol', action='store_const', dest='lang',
                      const='twol', help='Input is a TwoLC file')
    lang.add_argument('-x', '--xfst', action='store_const', dest='lang',
                      const='xfst', help='Input is an XFST file')
    args = parser.parse_args()

    if args.replace:
        replace_file(args.infile, args.outfile, args.replace, args.lang)
    else:
        print("Search isn't implemented yet")
