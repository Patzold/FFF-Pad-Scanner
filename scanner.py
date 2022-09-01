import os
import re
from tracemalloc import start
import requests
import argparse
import colorama
import time

URL_REGEX = "http[s]?\:\/\/pad\.fridaysforfuture\.(?:is|de)\/p\/[\w\.\-\%]+"
MAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
# "Some people, when confronted with a problem, think, 'I know, I'll use regular expressions.' Now they have two problems." - J. Zawinski

def get_pad_content(pad_name: str): # -> str
    """Lädt den Inhalt des Pads herunter
    
    Args:
        pad_name: name oder url des pads
    
    Returns:
        Inhalt das Pads als String
    """
    if "pad.fridaysforfuture.is" in pad_name:
        if pad_name[-1] != "/": pad_name += "/"
        url = pad_name + "export/txt"
    else: url = "https://pad.fridaysforfuture.is/p/" + pad_name + "/export/txt"
    
    try:
        response = requests.get(url)
        pad_content = response.text
    except Exception as e:
        print(colorama.Fore.RED + f"Exception in get_pad_content() while opening {url} \nOriginal Exception: {e}")
        pad_content = ""
    
    if pad_content == "Too many requests, please try again later.":
        print(colorama.Fore.RED + f"ACHTUNG - Zu viele requests für das Pad {pad_name} -> der Inhalt sowie alle Links des Pads werden nicht verarbeitet!")
        # "\033[31m" + "Hello" + "\033[0m"
    
    return pad_content

def search_for_urls(text: str, regex=URL_REGEX): # -> list
    """Durchsucht einen Text nach URLs
    
    Args:
        text: Der zu durchsuchende Text als String
    
    Returns:
        Eine Liste an gefundenen URLs (kann auch leer sein)
    """
    urls = re.findall(regex, text)
    
    # checken ob's eine URL zu einem FFF Pad ist
    pointer = 0
    while pointer < len(urls):
        if "pad.fridaysforfuture.is" not in urls[pointer]:
            urls.pop(pointer)
        else: pointer += 1
    
    return urls

def email_finder(text: str, regex=MAIL_REGEX): # -> list
    mail_adresses = re.findall(regex, text)
    return mail_adresses

def main(start: str, wait: int, text_path=None, urls_path=None, vs_path=None):
    """Ich behalte den Überblick.
    """
    pad_urls = {}
    url_queue = []
    vulnerabilities = []
    texts = []
    
    if start.endswith(".txt"):
        with open(start, "r") as reader:
            for line in reader:
                pad_name = line.replace("\n", "").strip()
                pad_urls[pad_name] = 1
                url_queue.append(pad_name)
    else:
        pad_urls[start] = 1
        url_queue.append(start)
    
    # url_queue beinhaltet alle noch abzuarbeitenden URLs
    while len(url_queue) > 0:
        current_url = url_queue.pop()
        time.sleep(wait)
        
        current_pad_text = get_pad_content(current_url)
        found_urls = search_for_urls(current_pad_text)
        
        for url in found_urls:
            pad_urls[url] = pad_urls.get(url, 0) + 1
            if pad_urls[url] == 1: url_queue.insert(0, url)
        
        texts.append([current_url, current_pad_text])
        
        mails = email_finder(current_pad_text)
        
        if len(mails) > 0:
            vulnerabilities.append([mails, current_url])
    
    # wenn gewünscht URLs als .txt ausgeben
    if urls_path is not None:
        if not os.path.isfile(urls_path):
            print(colorama.Fore.RED + f"ACHTUNG - Der Pfad {urls_path} zum speichern aller URLs existiert nicht!")
        else:
            with open(urls_path, "w") as writer:
                for url in pad_urls:
                    writer.write(url + "\n")
    
    # wenn gewünscht alle Texte der Pads als .txt ausgeben
    if text_path is not None:
        if not os.path.isfile(text_path):
            print(colorama.Fore.RED + f"ACHTUNG - Der Pfad {text_path} zum speichern aller Texte existiert nicht!")
        
        with open(text_path, "w") as writer:
            for t in texts:
                writer.write(f"\n--- Text aus dem Pad {t[0]} ---\n")
                writer.write(t[1])
    
    # wenn gewünscht alle Texte der Pads als .txt ausgeben
    if vs_path is not None:
        if not os.path.isfile(vs_path):
            print(colorama.Fore.RED + f"ACHTUNG - Der Pfad {vs_path} zum speichern aller Ergebnise existiert nicht!")
        
        with open(vs_path, "w") as writer:
            for v in vulnerabilities:
                writer.write(f"{v[0]} -> {v[1]}\n")
    else:
        print(vulnerabilities)

if __name__ == "__main__":
    colorama.init()
    parser = argparse.ArgumentParser(description="Durchsucht Pad(s) und alle verlinkten Pads. Muss mit mindestens --start oder --start_file ausgeführt werden. " + 
                                    "Tipp: wenn das Script öfters hintereinander ausgeführt wird, dran denken die .txt ouputs aufzuräumen und ggf. das --wait argument benutzen. " + 
                                    "Zum testen kann das Pad mit dem Namen pad_scanner_test genutzt werden.")
    
    parser.add_argument("-s", "--start", type=str,
                        help="Name oder URL zum Pad von dem aus die Suche starten soll",
                        default="pad_scanner_test")
    parser.add_argument("-sf", "--start_file", type=str,
                        help="Pfad zu einer .txt Datei die Namen oder URLs zu Pads beinhaltet, von denen eine Suche gestartet werden soll",
                        default=None)
    parser.add_argument("-w", "--wait", type=int,
                        help="Wartezeit in Sekunden zwischen jedem request",
                        default=0)
    parser.add_argument("-txt", "--text_path", type=str,
                        help="Wenn der gesammte Text aller Pads abgespeichert werden soll, gib hier einen Dateipfad an (.txt Datei)",
                        default=None)
    parser.add_argument("-urls", "--urls_path", type=str,
                        help="Wenn alle URLs zu den gefundenen Pads abgespeichert werden soll, gib hier einen Dateipfad an (.txt Datei)",
                        default=None)
    parser.add_argument("-vs", "--vulnerables_path", type=str,
                        help="Wenn alle gefundenen Mailadressen und Tel Nummern abgespeichert werden soll, gib hier einen Dateipfad an (.txt Datei)",
                        default=None)
    
    args = parser.parse_args()
    
    startarg = args.start_file
    if startarg is None: startarg = args.start
    
    main(startarg, args.wait, text_path=args.text_path, urls_path=args.urls_path, vs_path=args.vulnerables_path)
    # out = get_pad_content("https://pad.fridaysforfuture.is/p/Dortmund_gesammelte_Reden")
    # print(out)