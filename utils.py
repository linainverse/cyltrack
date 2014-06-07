import cgi

def escapeHTML(input):
  return cgi.escape(input, quote = True)
