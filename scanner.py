import os
import re
import requests
import argparse
import colorama
import time

URL_REGEX = "http[s]?\:\/\/pad\.fridaysforfuture\.(?:is|de)\/p\/[\w\.\-\%]+"
MAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
TEL_REGEX = r"[\d|\ |\-]{5,20}"
CLOUD_REGEX = r"cloud\.fridaysforfuture\.is/+[A-Za-z0-9.\&%/-]+"
FFFUTURE_REGEX = r"fffutu.re/[\w-]+"
WHATSAPP_REGEX = r"[A-Za-z0-9.-]+whatsapp\.com/+[A-Za-z0-9.\&%-]+"
WA_ME_REGEX = r"wa\.me/[A-Za-z0-9]+"
# "Some people, when confronted with a problem, think: 'I know, I'll use regular expressions.'
#  Now they have two problems."
#       - J. Zawinski

requests_counter = 0

def get_pad_content(pad_name: str, wait_for: int, wait_every: int): # -> str
    """Lädt den Inhalt des Pads herunter
    
    Args:
        pad_name: name oder url des pads
    
    Returns:
        Inhalt das Pads als String
    """
    global requests_counter
    if "pad.fridaysforfuture.is" in pad_name:
        if pad_name[-1] != "/": pad_name += "/"
        url = pad_name + "export/txt"
    else: url = "https://pad.fridaysforfuture.is/p/" + pad_name + "/export/txt"
    
    if requests_counter % wait_every == 0 and requests_counter != 0:
        time.sleep(wait_for)
    
    try:
        response = requests.get(url)
        pad_content = response.text
    except Exception as e:
        print(colorama.Fore.RED + f"Exception in get_pad_content() while \
            opening {url} \nOriginal Exception: {e}")
        pad_content = ""
    
    requests_counter += 1
    if requests_counter % 10 == 0:
        print(colorama.Fore.CYAN + f"INFO - {requests_counter} requests have been send")
    
    if pad_content == "Too many requests, please try again later.":
        print(colorama.Fore.RED + f"ACHTUNG - Zu viele requests für das Pad \
            {pad_name} -> der Inhalt sowie alle Links des Pads werden nicht verarbeitet!")
    print(requests_counter)
    
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
    """Durchsucht Text nach E-Mail Adressen
    
    Args:
        text: Der zu durchsuchende Text
        regex: [optional] eigene regular expression
    
    Returns:
        Liste mit gefundenen E-Mail Adressen
    """
    mail_adresses = re.findall(regex, text)
    return mail_adresses

def tel_finder(text: str, regex=TEL_REGEX): # -> list
    """Durchsucht Text nach Telefonnummern
    
    Args:
        text: Der zu durchsuchende Text
        regex: [optional] eigene regular expression
    
    Returns:
        Liste mit gefundenen Telefonnummern
    """
    regexout = re.findall(regex, text)
    out = []
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    for rex in regexout:
        if any(num in rex for num in numbers):
            out.append(rex)
    
    return out

def fff_links_finder(text: str, regex_cloud=CLOUD_REGEX, 
                     regex_fffuture=FFFUTURE_REGEX): # -> list
    """Durchsucht Text nach Links zur FFF Cloud oder dem FFF link shortener
    
    Args:
        text: Der zu durchsuchende Text
        regex_cloud: [optional] eigene regular expression für
                    chat.fridaysforfuture.is links
        regex_fffuture: [optional] eigene regular expression für
                    fffutu.re links
    
    Returns:
        Liste mit gefundenen E-Mail Adressen
    """
    links = re.findall(regex_cloud, text)
    links += re.findall(regex_fffuture, text)
    return links

def whatsapp_links_finder(text: str, regex_chat=WHATSAPP_REGEX,
                          regex_account=WA_ME_REGEX): # -> list
    """Durchsucht Text nach WhatsApp Links zu Gruppen / Chats / Personen
    
    Args:
        text: Der zu durchsuchende Text
        regex_chat: [optional] eigene regular expression für
                    chat.whatapp.com links
        regex_account: [optional] eigene regular expression für
                    wa.me links
    
    Returns:
        Liste mit gefundenen E-Mail Adressen
    """
    links = re.findall(regex_chat, text)
    links += re.findall(regex_account, text)
    return links

def references_to_marginalized_groups(text: str): # -> list
    """Durchsucht Text nach möglichen Verweisen auf Zugehörigkeit zu
    marginalisierten Gruppen.
    
    Args:
        text: Der zu durchsuchende Text
    
    Returns:
        Liste mit möglichen Referenzen
    """
    text = text.split("\n")
    
    results = []
    
    for i in range(len(text)):
        line = text[i]
        line = line.lower().strip()
        
        if "flinta" in line or "quotier" in line:
            results.append(text[i])
    
    return results

def write_text_line_by_line(text: str, path: str): # -> bool
    """Schreibt einen String Zeile für Zeile in eine Datei. Falls es dabei
    in einer Zeile zu einem Fehler kommt, wird diese einfach übersprungen.
    
    Args:
        text: String zum abspeichern
        path: Pfad zur .txt Datei
    """
    success = False
    text = text.split("\n")

    with open(path, "w") as writer:
        for line in text:
            try:
                writer.write(line + "\n")
                success = True
            except Exception as e:
                print(colorama.Fore.RED + f"Exception while saving line to "
                      + f"{path} \nOriginal Exception: {e}")
    
    if success:
        print(colorama.Fore.GREEN + f"Saving {path} (at least) partially sucessful.")

def output(path: str, urls: list, data: dict):
    """Schreibt die gesammelten Ergebnisse als .txt in ein Verzeichnis
    """
    if path[-1] != "/": path += "/"
    """
    with open(path + "urls.txt", "w") as writer:
        for url in urls:
            for line in url:
                try:
                    writer.write(line + "\n")
                except Exception as e:
                    print(colorama.Fore.RED + f"Exception while saving URLs to \
                        {path}urls.txt \nOriginal Exception: {e}")
    
    with open(path + "text.txt", "w") as writer:
        for indx, t in enumerate(data["text"]):
            try:
                writer.write(f"\n--- Text aus dem Pad {t[0]} ---\n")
                writer.write(t[1])
            except Exception as e:
                print(colorama.Fore.RED + f"Exception while saving texts to \
                    {path}urls.txt \nOriginal Exception: {e}")
                write_text_line_by_line(t[1], f"{path}text_{indx}.txt")
    
    with open(path + "results.txt", "w") as writer:
        try:
            writer.write(f"Gefundene E-Mailadressen:")
            writer.write(f"{v[0]} -> {v[1]}\n")
        except Exception as e:
            print(colorama.Fore.RED + f"Exception while saving results to \
                {path}results.txt \nOriginal Exception: {e}")
    """
    
    import json
    with open(path + "data.json", "w") as w:
        json.dump(data, w, indent=4)
    
    print(colorama.Fore.GREEN + f"Successfully saved data to {path}")

def main(start: str, wait: int, output_path: str, verbose=False,
         wait_for=0, wait_every=10, save_every=20):
    """Ich behalte den Überblick.
    """
    global requests_counter
    pad_urls = {}
    url_queue = []
    data = {"email": [], "tel": [], "wa": [], "links": [], "ref": [], "text": []}
    
    if start.endswith(".txt"):
        with open(start, "r") as reader:
            for line in reader:
                pad_name = line.replace("\n", "").strip()
                pad_urls[pad_name] = 1
                url_queue.append(pad_name)
    else:
        pad_urls[start] = 1
        url_queue.append(start)
    
    # try:
    while len(url_queue) > 0:
        current_url = url_queue.pop()
        time.sleep(wait)
        
        current_pad_text = get_pad_content(current_url, wait_for, wait_every)
        found_urls = search_for_urls(current_pad_text)
        
        for url in found_urls:
            escaped_url = url.replace("\u202a", "")
            pad_urls[escaped_url] = pad_urls.get(url, 0) + 1
            if pad_urls[escaped_url] == 1: url_queue.insert(0, url)
        
        # escape special characters
        current_pad_text = current_pad_text.replace("\\", "[\]")
        data["text"].append([current_url, current_pad_text])
        
        mails = email_finder(current_pad_text)
        tels = tel_finder(current_pad_text)
        fff_links = fff_links_finder(current_pad_text)
        whatsapp_links = whatsapp_links_finder(current_pad_text)
        references = references_to_marginalized_groups(current_pad_text)
        
        if len(mails) > 0:
            data["email"].append([mails, current_url])
        if len(tels) > 0:
            data["tel"].append([tels, current_url])
        if len(fff_links) > 0:
            data["links"].append([fff_links, current_url])
        if len(whatsapp_links) > 0:
            data["wa"].append([whatsapp_links, current_url])
        if len(references) > 0:
            data["ref"].append([references, current_url])
        
        if requests_counter % save_every == 0 and requests_counter != 0:
            output(output_path, pad_urls, data)
    # except Exception as e:
    #     print(colorama.Fore.RED + f"Exception in main loop while processing "
    #           + f"{current_url}\nOriginal Exception: {e}")
    
    output(output_path, pad_urls, data)

if __name__ == "__main__":
    colorama.init()
    parser = argparse.ArgumentParser(description="Durchsucht Pad(s) und alle \
            verlinkten Pads. Muss mit mindestens --start oder --start_file ausgeführt werden. \
            Tipp: wenn das Script öfters hintereinander ausgeführt wird, dran \
            denken die .txt ouputs aufzuräumen und ggf. das --wait argument benutzen. \
            Zum testen kann das Pad mit dem Namen pad_scanner_test genutzt werden.")
    
    parser.add_argument("-s", "--start", type=str,
                        help="Name oder URL zum Pad von dem aus die Suche starten soll",
                        default="pad_scanner_test")
    parser.add_argument("-sf", "--start_file", type=str,
                        help="Pfad zu einer .txt Datei die Namen oder URLs zu Pads beinhaltet, \
                            von denen eine Suche gestartet werden soll",
                        default=None)
    parser.add_argument("-w", "--wait", type=int,
                        help="Wartezeit in Sekunden zwischen jedem request",
                        default=0)
    parser.add_argument("-o", "--output", type=str,
                        help="Pfad zu einem Verzeichnis indem die Ergebnisse gespeichert werden. \
                            Der standard Pfad ist 'output/'. Bereits existierende Dateien werden überschrieben.",
                        default="output/")
    parser.add_argument("-v", "--verbose", type=bool,
                        help="Bei True werden die Ergebnisse auch im Terminal geprintet",
                        default=False)
    parser.add_argument("-wf", "--wait_for", type=int,
                        help="Wartezeit in Sekunden alle --every requests",
                        default=0)
    parser.add_argument("-e", "--every", type=int,
                        help="Anzahl an requests zwischen Wartezeit von --wait_for Sekunden",
                        default=10)
    parser.add_argument("--open_links", type=bool,
                        help="Öffnet alle gefunden FFF Cloud und fffutu.re \
                            Links in einem neuen Browserfenster",
                        default=False)
    parser.add_argument("--save_every", type=int,
                        help="Speichert die Ergebnisse während des Programmablaufs \
                            alle angegebene requests",
                        default=20)
    
    args = parser.parse_args()
    
    startarg = args.start_file
    if startarg is None: startarg = args.start
    
    main(startarg, wait=args.wait, output_path=args.output, verbose=args.verbose,
         wait_for=args.wait_for, wait_every=args.every)
    
    # python3 scanner.py -sf "start.txt" -w 5 -o "output" -wf 30 -e 10 --save_every 25