import requests, re, time, urllib.parse

import settings

def FindPads(filepath = "", baseurl = "", padnames = [], urlextention = "", regex = "", verbose = False, sleep = False):
	ParseChats(filepath, baseurl = baseurl, padnames = padnames, urlextention = urlextention, regex = regex, verbose = verbose, sleep = sleep)
	for name in padnames:
		if verbose:
			print("Pad", name, "durchsuchen")
		text = OpenPads(baseurl = baseurl, padname = name, urlextention = urlextention)
		ParseText(text, regex = regex, baseurl = baseurl, padnames = padnames, verbose = verbose)

		if sleep:
			time.sleep(5)

def OpenPads(baseurl = "", padname = "", urlextention = ""):
	url = baseurl + padname + urlextention
	result = requests.get(url)
	text = result.text
	return text

def ParseText(text, regex = "", baseurl= "", padnames = [], verbose = False):
	urls = re.findall(regex, text)
	for index, url in enumerate(urls):
		start = len(baseurl)
		padname = url[start:]
		padname = urllib.parse.unquote(padname) #%20 to Spaces etc.

		if padname not in padnames:
			if verbose:
				print(padname, "zu Pads hinzufügen")
			padnames.append(padname)

def ParseChats(filepath, baseurl = "", padnames = [], urlextention = "", regex = "", verbose = False, sleep = False):
	with open(filepath) as f:
		content = f.read()
	ParseText(content, regex = regex, baseurl= baseurl, padnames = padnames, verbose = False)

if __name__ == "__main__":
	import sys

	verbose = False
	sleep = True

	if len(sys.argv) > 1:
		for index, arg in enumerate(sys.argv[1:], 1):
			if arg == "-v":
				verbose = True
			elif arg == "-s":
				sleep = False

	padnames = settings.padnames

	FindPads(filepath = settings.filepath, baseurl = settings.baseurl, padnames = padnames, urlextention = settings.urlextention, regex = settings.regex, verbose = verbose, sleep = sleep)

	if verbose:
		print(len(padnames), " Pads gefunden")
		padnames.sort()
		print(padnames)