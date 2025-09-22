# pypolite/profanity.py
import re
import unicodedata
import os
import emoji

class SimpleChecker:
    _repeat_run_re = re.compile(r'([a-z])\1{1,}', flags=re.I)

    _LEET_MAP = {
        '@': ['a', 'u'],
        '4': ['a'],
        '3': ['e'],
        '1': ['i', 'l'],
        '0': ['o'],
        '$': ['s'],
        '+': ['t'],
        '!': ['i', 'l', ''],
        '7': ['t', 'l'],
        '5': ['s'],
        '%': ['x'],
        '&': ['and'],
        '#': ['h'],
        '?': ['q'],
        '.':[''],
        '-':[' '],
        "*": ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
    }

    _PUNCT_ENDINGS = set(['!', '.', '?', ',', ':', ';', ')', ']', '}', '"', "'"])

    def __init__(self, profanity_words=None, mode="word", max_consecutive=2, demojize=True):
        self.mode = mode
        self.demojize = demojize
        self.max_consecutive = max_consecutive

        if profanity_words is None:
            data_path = os.path.join(os.path.dirname(__file__), "data", "bad_words_cmu.txt")
            if not os.path.exists(data_path):
                raise FileNotFoundError(f"CMU bad word dataset not found at {data_path}")
            with open(data_path, encoding="utf-8") as f:
                self._raw_words = [line.strip() for line in f if line.strip()]
        elif isinstance(profanity_words, (list, tuple, set)):
            self._raw_words = list(profanity_words)
        else:
            raise ValueError("profanity_words must be None or an iterable of strings")

        self._compile()

    def _apply_leet_map(self, s, leet_map=None, max_count=1000):
        if not s:
            return s
        leet_map = leet_map or self._LEET_MAP
        out_tokens = []
        tokens = s.split()
        for tok in tokens:
            variants = set([tok])
            for sym, repls in leet_map.items():
                if not isinstance(repls, list):
                    repls = [repls]
                if not sym.isalnum():
                    repls = repls + ['']
                new_variants = set()
                for variant in variants:
                    for repl in repls:
                        esc = re.escape(sym)
                        # replace ALL occurrences in the variant
                        tmp = re.sub(rf'(?<=[A-Za-z]){esc}(?=[A-Za-z])', repl, variant)
                        tmp = re.sub(rf'(?<![A-Za-z]){esc}(?=[A-Za-z])', repl, tmp)
                        if sym not in self._PUNCT_ENDINGS:
                            tmp = re.sub(rf'(?<=[A-Za-z]){esc}(?![A-Za-z])', repl, tmp)
                        # If multiple occurrences, generate all combinations
                        tmp_variants = [tmp]
                        # Split by the symbol to get multiple positions
                        positions = [m.start() for m in re.finditer(re.escape(sym), variant)]
                        if len(positions) > 1:
                            # simple cross-product approach for small number of symbols
                            tmp_variants = set([variant])
                            for pos in positions:
                                temp_set = set()
                                for v in tmp_variants:
                                    for r in repls:
                                        temp_set.add(v[:pos] + r + v[pos+1:])
                                tmp_variants = temp_set
                        new_variants.update(tmp_variants)
                # truncate to max_count
                variants = set(list(new_variants)[:max_count])
            out_tokens.append(" ".join(variants))
        return " ".join(out_tokens)


    def _strip_diacritics(self, s):
        nkfd = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in nkfd if not unicodedata.combining(ch))

    def _collapse_spaced_letters_safe(self, text, min_letters=3, max_letters=12):
        if not text:
            return text
        sep = r'(?:[^A-Za-z]+?)'
        pattern = re.compile(
            rf'(?<![A-Za-z])'
            rf'(?:[A-Za-z](?:{sep}))'
            rf'{{{min_letters-1},{max_letters-1}}}'
            rf'[A-Za-z]'
            rf'(?![A-Za-z])',
            flags=re.IGNORECASE
        )
        def repl(m):
            span = m.group(0)
            return re.sub(r'\s+', '', span)
        return pattern.sub(repl, text)

    def _append_double_reduced_variant(self, token):
        def reduce_doubles(match):
            return match.group(1)
        reduced = self._repeat_run_re.sub(reduce_doubles, token)
        if reduced != token:
            return f"{token} {reduced}"
        return token

    def normalize_text(self, s, demojize=True, collapse_letter_spaces=True,
                        max_consecutive=2, apply_leet=True, generate_variants=True):
        if not s:
            return s
        s = unicodedata.normalize("NFKC", s)
        if demojize:
            s = emoji.demojize(s, language="en")
        s = self._strip_diacritics(s)
        s = s.lower()
        if collapse_letter_spaces:
            s = self._collapse_spaced_letters_safe(s)
        if apply_leet:
            s = self._apply_leet_map(s)
        if max_consecutive >= 1:
            s = re.sub(r'([a-z])\1{' + str(max_consecutive) + r',}',
                       lambda m: m.group(1) * max_consecutive, s, flags=re.I)
        s = re.sub(r'\s+', ' ', s).strip()
        tokens = s.split()
        tokens = [self._append_double_reduced_variant(tok) for tok in tokens]
        return " ".join(tokens)

    def _compile(self):
        if self.mode == "regex":
            self._patterns = [re.compile(p, flags=re.I) for p in self._raw_words]
        elif self.mode == "word":
            escaped = [re.escape(w) for w in self._raw_words if w.strip()]
            if escaped:
                pattern = r'\b(?:' + '|'.join(escaped) + r')\b'
                self._pattern = re.compile(pattern, flags=re.I)
            else:
                self._pattern = None
        else:
            raise ValueError("mode must be one of 'word' or 'regex'")

    def get_default_list(self):
        return list(self._raw_words)

    def replace_words(self, iterable):
        self._raw_words = list(iterable)
        self._compile()

    def extend_words(self, iterable):
        self._raw_words.extend(iterable)
        self._compile()

    def load_from_file(self, path, encoding='utf-8'):
        with open(path, encoding=encoding) as fh:
            words = [line.strip() for line in fh if line.strip() and not line.startswith('#')]
        self.replace_words(words)

    def contains_profanity(self, text):
        if not text:
            return False
        normalized = self.normalize_text(text, demojize=self.demojize,
                                            collapse_letter_spaces=True,
                                            max_consecutive=self.max_consecutive)
        
        print("Normalized text:", normalized)  # Debug statement

        if self.mode == "regex":
            return any(p.search(normalized) for p in self._patterns)
        elif self.mode == "word":
            tokens = re.findall(r'\b\w+\b', normalized)
            if not self._pattern:
                return False
            return bool(self._pattern.search(normalized))
        return False

checker = SimpleChecker()
test_sentences = ["fuuck", "hello", "sh!t", "d@mn", "This is a clean sentence.", "You are a b@stard!", "You are a 😠 person"]
for sentence in test_sentences:
    print(f"Input: {sentence}")
    print(f"Contains profanity? {checker.contains_profanity(sentence)}")
    print("-" * 40)