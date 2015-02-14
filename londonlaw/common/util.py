import re

def escape_chars(token):
   return re.sub(r"""("|\\)""", r"\\\1", token)

def add_quotes(token):
   if re.search(r"\s", token):
      return "".join(('"', token, '"'))
   else:
      return token

def join_tokens(*tokens):
   tokens = [escape_chars(token) for token in tokens]
   tokens = [add_quotes(token) for token in tokens]
   return " ".join(tokens)

def parse_bool(str):
   str = str.lower()
   if str == "true":
      return True
   elif str == "false":
      return False
   raise ValueError("invalid boolean value: %s" % str)

_nick_re = re.compile(r"^[^\n\t\"]+$")
def validate_nick(nick):
   if len(nick) > 25:
      raise ValueError("nick too long")
   if not _nick_re.match(nick):
      raise ValueError("illegal format for player nick")
   return nick

# arch-tag: f95a921b-7e45-4d54-9273-ae670d7ac93f
