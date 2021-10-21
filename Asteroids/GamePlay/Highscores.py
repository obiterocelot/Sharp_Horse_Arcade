import ast
import os

#make sure if you are clearing the dictionary for whatever reason to leave {} so the file knows its a dictionary

def get_dict():
    """pulls dictionary from text document and turns it into a readable dictionary in programme"""
    with open(os.path.join(os.path.dirname(__file__), 'highscores.txt'), 'r+') as f:
        data = f.read()
        fulldict = ast.literal_eval(data) # pulling the text in the document as a dictionary
        return fulldict

def append_dict(fulldict):
    """rewrites the dictionary with the new changes"""
    with open(os.path.join(os.path.dirname(__file__), 'highscores.txt'), 'r+') as f:
        f.truncate(0)
        f.seek(0) #may not be fully necessary, but help reset the file
        f.write(str(fulldict))

def add_to_highscores(score, text):
    """adds the new highscore to the dictionary"""
    fulldict = get_dict()
    fulldict[text] = score #sets new the dictionary object format
    #sorts the dictionary into reverse order. The sort creates tuples, but we need to turn them back into a dictionary.
    #hense the {x:y for x, y} stuff
    sorted_dict = {x: y for x, y in sorted(fulldict.items(), key=lambda item: item[1], reverse=True)}
    append_dict(sorted_dict)


