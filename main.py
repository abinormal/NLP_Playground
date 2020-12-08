# Main python file to get contents of text files and output the most frequent "interesting words"

from page import head, tail
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from argparse import ArgumentParser
from os import path
import sys
import glob
import re
import nltk
# nltk.download()  # uncomment to download nltk packages - only once


def fGetWordnetPos(word):
    # Map POS tag to first character lemmatize() accepts
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tagDict = {"J": wordnet.ADJ,
               "N": wordnet.NOUN,
               "V": wordnet.VERB,
               "R": wordnet.ADV}

    return tagDict.get(tag, wordnet.NOUN)


def fLemmatize(string):
    # Returns lemmatized token list
    lemmatizer = WordNetLemmatizer()
    tokens = ([lemmatizer.lemmatize(w, fGetWordnetPos(w))
               for w in word_tokenize(string)])
    return tokens


def fCleanString(fileContents):
    # Make lower case, remove punctuation, lemmatize, split into token and remove stop words
    fileContents = fileContents.lower()
    string = re.sub(r'\W+', ' ', fileContents)
    tokens = fLemmatize(string)
    # Remove stopwords
    return fStopWords(tokens)


def fStopWords(words):
    # Removes stop words
    stop_words = set(stopwords.words('english'))
    # Add more words to the list
    more_words = ['new', 'make', 'time', 'work', 'one', 'know', 'say', 'let', 'care', 'last', 'way', 'like', 'get', 'keep', 'give', 'could', 'way', 'come', 'well', 'need',
                  'see', 'go', 'take', 'must', 'many', 'also', 'u', 'want', 'come', 'think', 'today', 'every', 'even', 'told', 'two', 'long', 'tell', 'call', 'back', 'first',
                  'hard', 'day', 'end', 'look', 'saw']
    for w in more_words:
        stop_words.add(w)
    filteredWords = []
    for word in words:
        if not word in stop_words:
            filteredWords.append(word)
    return filteredWords


def fGetMostFrequent(allWords, numResults):
    # Returns a Dictionary of word, number
    freq = nltk.FreqDist(allWords)
    # Sort by value in decending order
    interestingWords = []
    for w in sorted(freq, key=freq.get, reverse=True):
        interestingWords.append([w, freq[w]])
    # Get top results - numResults
    mostFrequent = []
    for x in range(0, numResults):
        mostFrequent.append(interestingWords[x])
    return mostFrequent


def fGetAllWords(files):
    # Returns all words from a file
    words = []
    for currentFile in files:
        with open(currentFile, encoding="utf8") as f:
            string = f.read()
        words += (fCleanString(string))
    return words


def fGetFilesSentences(files, words):
    # Return a dictionary of all files and strings where word is found
    d = {}
    for currentFile in files:
        with open(currentFile, encoding="utf8") as f:
            fileString = f.read()
        sentences = sent_tokenize(fileString)
        for word in words:
            for sentence in sentences:
                # (?i) - case insensitive match
                pattern = r'(?i)\b{}\b'.format(word[0])
                # TODO - Wrap <b></b> around the found word
                if (re.findall(pattern, sentence)):
                    # strip the filename from the path
                    fpath, ftail = path.split(currentFile)
                    d.setdefault(word[0], []).append(
                        [[ftail], [sentence.strip()]])
    return d


# CLI
parser = ArgumentParser(
    description='Given a directory, pull out the interesting words and display')
parser.add_argument("directory", type=str,
                    help="Name of the directory")  # Not optional
parser.add_argument("-o", "--output", dest="output", type=str,
                    help="Name of the output file", default="interesting")  # optional
parser.add_argument("-n", "--results", dest="results", type=int,
                    help="Number of interesting words to output", default=5)  # optional

args = parser.parse_args()
inputDir = args.directory
outputName = args.output
numResults = args.results
if not (path.exists(inputDir)):
    print("Directory not found")
    sys.exit()

# Get all text files in the directory
fileList = glob.glob(".\{0}\*.txt".format(inputDir))

if not (fileList):
    print("Only accepts text files")
    sys.exit()

print("Using '{}' the top {} interesting words can be found in '{}.html'".format(
    inputDir, numResults, outputName))

# Process files:
# Get number(numResults) of most frequent results
frequentWords = fGetMostFrequent(fGetAllWords(fileList), numResults)

# Extract locations and sentences
dResults = fGetFilesSentences(fileList, frequentWords)


# Create table:
table = ''
for word in frequentWords:
    setoffiles = set()
    setofsentences = set()
    # start row + 1st column <tr><td>word(frequency)</td> ..
    table += '''<tr><td>{} ({})</td>'''.format(word[0], word[1])
    fileSentence = (dResults.get(word[0]))
    for fs in fileSentence:
        setoffiles.add(fs[0][0])
        setofsentences.add(fs[1][0])
    # 2nd column <td><p>filenames</p></td>
    table += '''<td>'''
    for f in setoffiles:
        table += '''<p>{}</p>'''.format(f)
    table += '''</td>'''
    # 3rd column <td><p>sentences</p></td>
    table += '''<td>'''
    for s in setofsentences:
        table += '''<p>{}</p>'''.format(s)
    table += '''</td>'''
    # end of row
    table += '''</tr>'''

# Open new file, write doc to it and close
destinationFile = outputName+".html"
f = open(destinationFile, "w")
f.write(head+table+tail)
f.close()
