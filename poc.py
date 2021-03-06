# A proof of concept command line program that can download text files, load
# them locally, or use a string as text, and tokenizes the text using spacy,
# provididng a couple commands to print the text, list the entities, and list
# and filter the tokens.

# Example usage:

# https://asciinema.org/a/Sc7jFZJx7DkWKRGnJRbheAEx3

import re
import requests
import readline
import os
import atexit

# This takes a bit to load, so why not print a message to show everything's ok
print("Importing spacy...")
import spacy



# You can ignore this, it's taken straight from:
# https://docs.python.org/3/library/readline.html

def save(prev_h_len, histfile):
    new_h_len = readline.get_current_history_length()
    readline.set_history_length(1000)
    readline.append_history_file(new_h_len - prev_h_len, histfile)


# This looks silly now, but later you may want to do more complicated things on
# exit, and you can add them to one place: right here, instead of having to go
# into every place the program exits and copying code.
def goodbye():
    print("Ciao!")

def main():

    # This too is from the above link, it's just to make the command line
    # interface a little cleaner/easier to work with.
    histfile = os.path.join(os.path.expanduser("~"), ".poc_history")

    try:
        readline.read_history_file(histfile)
        h_len = readline.get_current_history_length()
    except FileNotFoundError:
        open(histfile, 'wb').close()
        h_len = 0

    atexit.register(save, h_len, histfile)

    readline.set_history_length(5000)

    ### START OF MAIN PROGRAM

    # We'll store our texts to analyze in a dictionary
    texts = {}

    # Print some messages before loading models, since it takes a second
    print("Loading english language model...")
    nlp_en = spacy.load('en_core_web_sm')
    print("Cargando modelo del español...")
    nlp_es = spacy.load("es_core_news_sm")


    # Function to add a named document to the texts dictionary
    def add_to_dict(name, lang, text):
        if lang == "es":
            texts[name] = nlp_es(text)
        elif lang == "en":
            texts[name] = nlp_en(text)
        # Default to english if language unknown
        else:
            texts[name] = nlp_en(text)



    # Main program loop
    while True:
        # print(texts)
        try: # Try to read an input from user as string
            cmd = input("[poc]> ").strip()
        except EOFError: # In case the user hits CTRL-D, just quit and stop
            break
        if not cmd: # No user input, emptry strings in python are 'falsey'
            continue
        # Regex match quit command, case insensitive, stop loop
        elif m := re.match(cmd, "quit", flags=re.IGNORECASE):
            break

        # Regex match download command, example: test_text en download https://example.com
        # This downloads the text, processes it with the correct nlp function,
        # and stores a text into our dictionary
        elif m := re.match("(?P<text>\S+)\s+(?P<lang>\w+)\s+download\s+(?P<url>.+)", cmd):
            try:
                r = requests.get(m.group("url"))
            except requests.exceptions.InvalidSchema:
                print("Please enter a valid download url!")
                continue
            else:
                add_to_dict(m.group("text"), m.group("lang"), r.text)

        # Regex match file command, example: test_text en file some_file
        # Same as donwload, but uses a local file instead
        elif m := re.match("(?P<text>\S+)\s+(?P<lang>\w+)\s+file\s+(?P<filename>.+)", cmd):
            with open(m.group("filename")) as f:
                add_to_dict(m.group("text"), m.group("lang"), f.read())

        # Regex match string command, example: test_text en string Hello, my name is Diego
        # Same as above, but uses a string instead
        elif m := re.match("(?P<text>\S+)\s+(?P<lang>\w+)\s+string\s+(?P<str>.+)", cmd):
                add_to_dict(m.group("text"), m.group("lang"), m.group("str"))

        # Regex match print command, example: test_text print
        elif m := re.match("(?P<text>\S+)\s+(print|text)", cmd):
            text = m.group("text")
            if text not in texts:
                print("No such text")
                continue
            print(texts[text])

        # Regex match entitiy command
        elif m := re.match("(?P<text>\S+)\s+(ents|entities)", cmd):
            text = m.group("text")
            if text not in texts:
                print("No such text")
                continue
            text = texts[text]
            pad = max(len(ent.text) for ent in text.ents)
            for ent in text.ents:
                print(ent.text.ljust(pad), ent.label_)

        elif m := re.match("(?P<text>\S+)\s+pos( (?P<pos>\w+))?( (?P<lemma>lemma))?", cmd):
            text = m.group("text")
            if text not in texts:
                print("No such text")
                continue
            text = texts[text]
            pad = max(len(tok.text) for tok in text)
            pos = m.group("pos")
            print(pos)
            for token in text:
                if pos and token.pos_ == pos:
                    print(token.text.ljust(pad), token.pos_,
                           token.lemma_ if m.group("lemma") else "")
                elif not pos:
                    print(token.text.ljust(pad), token.pos_,
                          token.lemma_ if m.group("lemma") else "")

        else:
            print("Invalid command!")


        # elif cmd[0] in texts:
            # pass

    # Finalize the program
    goodbye()


if __name__ == '__main__':
    main()
