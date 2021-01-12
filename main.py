#! /usr/bin/env python3

# Main python file to get contents of text files and output the most frequent "interesting words"

import datetime
from page import head, middle, tail
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from argparse import ArgumentParser
from os import path
import webbrowser
import ntpath
import sys
import glob
import re
import nltk
# nltk.download()  # uncomment to download nltk packages - only once


def get_wordnet_pos(word):
    # Map POS tag to first character lemmatize() accepts
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tagDict = {"J": wordnet.ADJ,
               "N": wordnet.NOUN,
               "V": wordnet.VERB,
               "R": wordnet.ADV}

    return tagDict.get(tag, wordnet.NOUN)


def lemmatize(string):
    # Returns lemmatized token list
    lemmatizer = WordNetLemmatizer()
    tokens = ([lemmatizer.lemmatize(w, get_wordnet_pos(w))
               for w in word_tokenize(string)])
    return tokens


def clean_string(fileContents):
    # Make lower case, remove punctuation, lemmatize, split into token and remove stop words
    fileContents = fileContents.lower()
    string = re.sub(r'\W+', ' ', fileContents)
    tokens = lemmatize(string)
    # Remove stopwords
    return stop_words(tokens)


def stop_words(words):
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


def get_most_frequent(allWords, numResults):
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


def read_file(file_name):
    try:
        with open(file_name, encoding="utf8") as f:
            string = f.read()
        return string
    except IOError as error:
        print("Caught IOError: {}".format(error))


def get_all_words(files):
    # Returns all words from a file
    words = []
    for currentFile in files:
        string = read_file(currentFile)
        words += (clean_string(string))
    return words


def get_files_sentences(files, words):
    # Return a dictionary of all files and strings where word is found
    d = {}
    for currentFile in files:
        fileString = read_file(currentFile)
        sentences = sent_tokenize(fileString)
        for word in words:
            for sentence in sentences:
                # (?i) - case insensitive match
                pattern = r'(?i)\b{}\b'.format(word[0])
                # TODO - Wrap <b></b> around the found word
                if (re.findall(pattern, sentence)):
                    # Alter sentence to put <b> tags round the word
                    src_str = re.compile(word[0], re.IGNORECASE)
                    sentence = src_str.sub("<b>"+word[0]+"</b>", sentence)
                    # strip the filename from the path
                    fpath, ftail = path.split(currentFile)
                    # Add info to dict
                    d.setdefault(word[0], []).append(
                        [[ftail], [sentence.strip()]])
    return d


def command_line():
    parser = ArgumentParser(
        description='Given a directory of .txt files, pull out the interesting words and display in HTML.')
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

    filePath = path.join(".", inputDir, "*.txt")
    fileList = glob.glob(filePath)

    if not (fileList):
        print("Only accepts text files")
        sys.exit()

    print("Using '{}' the top {} interesting words can be found in '{}.html'. This will open automatically once processed".format(
        inputDir, numResults, outputName))
    # Get info for the output
    currentDT = datetime.datetime.now()
    info = "<p>On the {} at {}, the top {} interesting words were found in the directory '{}' in these files:</p>".format(
        currentDT.strftime("%dth of %B %Y"), currentDT.strftime("%I:%M"), numResults, inputDir)
    info += "<ul>"
    for f in fileList:
        info += "<li>" + ntpath.basename(f) + "</li>"
    info += "</ul>"

    return info, fileList, numResults, outputName


def main():
    # get user instructions
    info, fileList, numResults, outputName = command_line()
    # Process files:
    # Get number(numResults) of most frequent results
    frequentWords = get_most_frequent(get_all_words(fileList), numResults)

    # Add more information to the output
    info += "<p>The most frequent interesting words found are: </p><ol>"
    for w in frequentWords:
        info += '''<li><a href="#{}">{}({})</a></li>'''.format(
            w[0], w[0].capitalize(), w[1])
    info += "</ol>"

    # Extract locations and sentences
    dResults = get_files_sentences(fileList, frequentWords)

    # Create table:
    table = ''
    for word in frequentWords:
        setoffiles = set()
        setofsentences = set()
        # start row + 1st column <tr><td>word(frequency)</td> ..
        table += '''<tr ><td ><h3><span id = "{}"></span>{} ({})</h3><p><a href="#top">Back</a></p></td>'''.format(
            word[0], word[0].capitalize(), word[1])
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
    f.write(head+info+middle+table+tail)
    f.close()
    print("Opening generated file '{}'".format(destinationFile))
    webbrowser.open_new_tab(destinationFile)


if __name__ == "__main__":
    main()
