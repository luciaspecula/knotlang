#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-тест КНОТЛАНГ v0.6.3 — бытовое ядро и фонология.

ВНИМАНИЕ: это smoke-тест, а не вычитыватель словаря. Список ROOTS задан
вручную и синхронизируется со словарём вручную (при изменении dictionary_v0.6.md
обновлять ROOTS здесь). Кандидаты (knot_parts_v0.6.md, interjections_v0.6.md)
в список НЕ входят — они не норматив. Междометия (звуки-жесты) не флектируются
и в проверках омонимии как корни не участвуют.

Проверяет:
  1. У каждого нормативного корня ровно 4 РАЗНЫЕ формы слоёв (исключение:
     предельные fix-слова nul/vit — все формы совпадают).
  2. Фонологию всех форм: нет 3+ гласных подряд, нет 3+ согласных подряд
     (по звукам: диграфы sh/ch = один согласный), нет запрещённых кластеров,
     двойные согласные — только tt/kk (+ задокументированные исключения).
  3. Отсутствие омонимических коллизий между формами разных корней.
  4. Суффиксную модель: помеченные CVC-корни дают формы на -i/-u/-a/-e.
  5. Запреты: zult не входит в составные числа; тройное повторение основы
     запрещено (кроме числового сокращения pa-pan и т.п.).

Запуск:  python3 tests/test_knotlang.py
Выход:   0 — все проверки прошли; 1 — найдены ошибки.
"""

VOWELS = "aeiou"
DIGRAPHS = ("sh", "ch", "ts", "zh")  # диграф = один согласный звук

# Двойные согласные внутри формы: разрешены tt/kk + исключения (задокументированы)
DOUBLE_OK = {"tt", "kk", "nn"}  # nn — только venn (кандидат консилиума)
DOUBLE_EXCEPTIONS = {"vennu", "venni", "venna", "venne"}  # venn: nn внутри основы

# Корни: модель + формы [зреет, держится, отдаётся, откликается]
# Модели: "A-t" (тип A на -t, флексия), "B" (тип B, суффиксы),
#         "suff" (суффиксная подмодель для CVC), "vowel" (основа на гласную),
#         "fix" (неизменяемое/предельное), "hist" (историческая форма)
ROOTS = {
    # --- Ядро канона (Часть II) ---
    "knot": ("A-t", ["knit", "knut", "knat", "knet"]),
    "okn":  ("suff", ["okni", "oknu", "okna", "okne"]),
    "grad": ("B", ["gradi", "gradu", "grada", "grade"]),
    "sen":  ("A-t", ["sint", "sunt", "sant", "sent"]),
    "nul":  ("fix", ["nul", "nul", "nul", "nul"]),
    "vit":  ("fix", ["vit", "vit", "vit", "vit"]),  # предельное слово (легенда vit)
    "tish": ("B", ["tishit", "tishut", "tishat", "tishet"]),  # шипящие: наращение -t
    "vel":  ("A-t", ["vilt", "vult", "valt", "velt"]),
    "var":  ("A-t", ["virt", "vurt", "vart", "vert"]),
    "kafe": ("B", ["kafei", "kafeu", "kafea", "kafee"]),  # морф. искл.: удвоение
    # --- Бытовое ядро (§15) ---
    "sut":  ("A-t", ["sit", "sut", "sat", "set"]),
    "pit":  ("A-t", ["pit", "put", "pat", "pet"]),
    "hod":  ("suff", ["hodi", "hodu", "hoda", "hode"]),
    "rech": ("B", ["rechi", "rechu", "recha", "reche"]),
    "zret": ("B", ["zreti", "zretu", "zreta", "zrete"]),
    "chut": ("B", ["chuti", "chutu", "chuta", "chute"]),
    "mat":  ("A-t", ["mit", "mut", "mat", "met"]),
    "tat":  ("A-t", ["tit", "tut", "tat", "tet"]),
    "det":  ("A-t", ["dit", "dut", "dat", "det"]),
    "rad":  ("suff", ["radi", "radu", "rada", "rade"]),
    "tug":  ("suff", ["tugi", "tugu", "tuga", "tuge"]),
    "trep": ("B", ["trepi", "trepu", "trepa", "trepe"]),
    "bol":  ("suff", ["boli", "bolu", "bola", "bole"]),
    "den":  ("suff", ["deni", "denu", "dena", "dene"]),
    # --- Связки (§13) ---
    "rawi": ("vowel", ["rawi", "rawu", "rawa", "rawe"]),
    "hel":  ("A-t", ["hilt", "hult", "halt", "helt"]),
    "kvel": ("B", ["kveli", "kvelu", "kvela", "kvele"]),
    "plet": ("B", ["pleti", "pletu", "pleta", "plete"]),
    "drem": ("B", ["dremi", "dremu", "drema", "dreme"]),
    # --- Миро/роды ---
    "kor":  ("suff", ["kori", "koru", "kora", "kore"]),
    "gor":  ("suff", ["gori", "goru", "gora", "gore"]),
    "neb":  ("suff", ["nebi", "nebu", "neba", "nebe"]),
    "venn": ("suff", ["venni", "vennu", "venna", "venne"]),
    "pret": ("suff", ["preti", "pretu", "preta", "prete"]),
    "cha":  ("vowel", ["chai", "chau", "chaa", "chae"]),
    "ptah": ("B", ["ptahi", "ptahu", "ptaha", "ptahe"]),  # фонет. искл. (pt)
}

# Исторические формы (не должны участвовать в коллизиях как норма, но фонологию проходят)
HISTORICAL = ["vultu", "wulte", "sent", "vedru", "vedra", "kniu"]

# Частично зафиксированные корни (не полнофлективные — в полный ROOTS не входят)
PARTIAL_ROOTS = {
    "mil": ["mil", "milt"],  # канон фиксирует только -u- (mil) и -i- (milt); полный ряд — открытый вопрос
}

# Междометия (звуки-жесты, вне морфологии): не флектируются, в омонимии не участвуют
INTERJECTIONS = ["kve", "mu", "ah", "oh", "eh"]  # кандидаты служебного слоя (interjections_v0.6.md)

# Числовые формы (базовые + конструкции)
NUMBERS = {
    "0": "zult", "1": "nult", "2": "duut", "3": "dunult", "4": "du-duut",
    "5": "pant", "5m": "pan", "10": "duult-pan", "25": "pa-pan",
    "26": "pa-pan+nult", "100": "du-duut-pa-pan", "125": "pa-pa-pan",
    "135": "(pa-pan+duult)-pan", "3125": "pa-pa-pa-pa-pan",
}

errors = []


def sounds(word):
    """Слово как последовательность звуков: диграфы схлопываются в один."""
    w = word.lower().replace("-", "").replace("+", "").replace("(", "").replace(")", "")
    out = []
    i = 0
    while i < len(w):
        two = w[i:i+2]
        if two in DIGRAPHS:
            out.append(two)
            i += 2
        else:
            out.append(w[i])
            i += 1
    return out


def vowel_clusters(snd):
    """Максимальная длина подряд идущих гласных звуков."""
    best = cur = 0
    for s in snd:
        if s in VOWELS:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def consonant_clusters(snd):
    """Максимальная длина подряд идущих согласных звуков."""
    best = cur = 0
    for s in snd:
        if s not in VOWELS:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def check_phonology(word, where):
    # Маркеры -, +, () — границы/паузы: кластеры считаем по сегментам,
    # внутри сегмента согласные соединяются, через маркер — нет (просодия: пауза как слой).
    segments = []
    for part in word.replace("(", " ").replace(")", " ").replace("+", " ").split():
        for sub in part.split("-"):
            segments.append(sub)
    for seg in segments:
        snd = sounds(seg)
        if vowel_clusters(snd) >= 3:
            errors.append(f"[фонология] {where} «{word}» (сегмент «{seg}»): 3+ гласных подряд")
        if consonant_clusters(snd) >= 3:
            errors.append(f"[фонология] {where} «{word}» (сегмент «{seg}»): 3+ согласных подряд (по звукам)")
        # двойные согласные внутри сегмента
        for i in range(len(snd) - 1):
            a, b = snd[i], snd[i+1]
            if a == b and a not in VOWELS and a not in DIGRAPHS and (a + a) not in DOUBLE_OK and word not in DOUBLE_EXCEPTIONS:
                errors.append(f"[фонология] {where} «{word}»: двойной согласный «{a}{a}» (разрешены tt/kk)")
                break
    whole = word.lower().replace("-", "").replace("+", "").replace("(", "").replace(")", "")
    # запрещённые начальные кластеры: pt- (кроме ptah)
    if whole.startswith("pt") and not whole.startswith("ptah"):
        errors.append(f"[фонология] {where} «{word}»: начальный кластер pt (запрещён, кроме ptah)")
    for bad in ("stk", "ptl"):
        if bad in whole:
            errors.append(f"[фонология] {where} «{word}»: запрещённое сочетание {bad}")


# 1. Четыре разные формы у каждого корня + фонология
for root, (model, forms) in ROOTS.items():
    if len(forms) != 4:
        errors.append(f"[формы] корень {root}: ожидается 4 формы, получено {len(forms)}")
    # повторяющиеся нормативные формы внутри корня (кроме предельных fix)
    if model != "fix" and len(set(forms)) != 4:
        errors.append(f"[формы] корень {root}: повторяющиеся формы {forms}")
    for f in forms:
        check_phonology(f, f"форма {root}")
    if root in ("nul", "vit") and model == "fix":
        if len(set(forms)) != 1:
            errors.append(f"[формы] предельное слово {root} должно не изменяться")
# частичные корни: фонология зафиксированных форм
for root, forms in PARTIAL_ROOTS.items():
    for f in forms:
        check_phonology(f, f"частичный корень {root}")

# 2. Фонология чисел и исторических форм
for label, num in NUMBERS.items():
    check_phonology(num, f"число {label}")
for h in HISTORICAL:
    check_phonology(h, "историческая")

# 3. Коллизии форм
seen = {}
for root, (model, forms) in ROOTS.items():
    for f in forms:
        if f in seen and seen[f] != root:
            errors.append(f"[коллизия] форма «{f}» у корней {seen[f]} и {root}")
        seen[f] = root
# числа не должны совпадать с формами корней (кроме закреплённых: pant/pan — число 5)
number_forms = set(NUMBERS.values())
number_words = set()
for n in number_forms:
    for part in n.replace("(", "").replace(")", "").split("+"):
        for p in part.split("-"):
            number_words.add(p)
collide = set(seen) & number_words
allowed_collide = {"pan", "pant", "duut", "nult", "zult", "dunult", "nul"}
bad = collide - allowed_collide
for w in sorted(bad):
    errors.append(f"[коллизия] форма корня «{w}» совпадает с числовым словом")

# 4. Суффиксная модель: формы оканчиваются на -i/-u/-a/-e (кроме историч. kafee)
for root, (model, forms) in ROOTS.items():
    if model == "suff":
        for f in forms:
            if not f.endswith(("i", "u", "a", "e")):
                errors.append(f"[суфф. модель] {root}: «{f}» не оканчивается на гласную слоя")
    if model == "vowel":
        endings = [f[-1] for f in forms]
        if endings != ["i", "u", "a", "e"]:
            errors.append(f"[подмодель на гласную] {root}: окончания {endings} ≠ i,u,a,e")

# 5. Запреты
# zult не входит в составные числа
for label, num in NUMBERS.items():
    if label not in ("0",) and "zult" in num:
        errors.append(f"[запрет] zult в составном числе {label} = {num}")
# тройное повторение основы запрещено (композиты); числовое сокращение pa-pan допустимо
COMPOSITES_OK = ["kni-multu", "tish-duut", "rod-kni", "tish-duut-rod", "kni-vult",
                 "kni-vult-multa", "du-duut", "du-duut-pa-pan", "kni multu",
                 "vit pa-pan", "pa-pa-pan"]
for c in COMPOSITES_OK:
    parts = c.replace("+", "-").replace("(", "").replace(")", "").split("-")
    for p in parts:
        # тройное повторение одной основы подряд — запрещено
        if parts.count(p) >= 3:
            errors.append(f"[запрет] тройное повторение основы «{p}» в {c}")
# Стражи: запрещённые конструкции не должны встречаться среди нормативных форм
FORBIDDEN_COMPOSITES = ["kni-kni-kni", "kni-kni-multu", "zult-pa-pa-pan"]
all_normal_forms = set()
for root, (model, forms) in ROOTS.items():
    all_normal_forms.update(forms)
all_normal_forms.update(NUMBERS.values())
for c in FORBIDDEN_COMPOSITES:
    if c in all_normal_forms:
        errors.append(f"[запрет] запрещённая конструкция «{c}» присутствует в норме")

if errors:
    print(f"FAIL: {len(errors)} ошибок")
    for e in errors[:40]:
        print("  -", e)
    raise SystemExit(1)
else:
    print(f"OK: {len(ROOTS)} корней, все формы фонологичны, коллизий нет, запреты соблюдены")
    raise SystemExit(0)
