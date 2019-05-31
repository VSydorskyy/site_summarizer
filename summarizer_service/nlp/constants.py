class Constants:
    WORD_TRESH = 20
    SENT_TRESH_INITIAL = 10
    SENT_TRESH_FINAL = 20

    ALPHABETS = "([A-Za-z])"
    PREFIXES = "(Mr|St|Mrs|Ms|Dr)[.]"
    SUFFIXES = "(Inc|Ltd|Jr|Sr|Co)"
    STARTERS = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    ACRONYMS = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    WEBSITES = "[.](com|net|org|io|gov)"