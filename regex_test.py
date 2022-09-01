import re

text = "https://docs.python.org/3/library/re.html achtung@beispiel.de hier ist ein weiterer test@fridaysforfuture.de for your convenience jon-doe@oh-no.gov"

# REGEX = r"[\w\.-]+@[\w\.-]+(\.[\w]+)+"
# REGEX = r"[a-zA-Z0-9]@[a-zA-Z0-9]"
REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

out = re.findall(REGEX, text)
print(out)