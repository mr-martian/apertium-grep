# apertium-grep
search and replace tools for Apertium source files

Dependencies:
```bash
$ pip3 install tree-sitter-apertium
```

Orthography Conversion:
```
$ apertium-grep/apertium-grep.py -t -r 'b / ב' -r 'g / ג' -r 'd / ד' -r 'h / ה' -r 'w / ו' -r 'z / ז' -r 'x / ח' -r 'v / ט' -r 'y / י' -r 'k / כ' -r 'l / ל' -r 'm / מ' -r 'n / נ' -r 's / ס' -r 'p / פ' -r 'c / צ' -r 'q / ק' -r 'r / ר' -r '%{s%} / שׂ' -r '%{sh%} / שׁ' -r 't / ת' -r 'a / ַ' -r 'á / ָ' -r 'e / ֵ' -r 'é / ֶ' -r 'i / ִ' -r 'o / ֹ' -r 'u / ֻ' -r '%@ / ְ' -r 'ä / ֲ' -r 'ë / ֱ' -r 'ö / ֳ' -r '. / ּ' -r "%' / א" -r "%{'%} / ע" apertium-hbo/apertium-hbo.hbo-ortho.twol blah
$ mv blah apertium-hbo/apertium-hbo.hbo-ortho.twol 
```
