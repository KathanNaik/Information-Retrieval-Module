# Importing all relavent Modules in Python
import functools
import os
import sys
import string
import webbrowser

os.system("pip install nltk")
print(os.getcwd())

from nltk.tokenize import sent_tokenize, word_tokenize


# Porter's Stemming Algorithm Class containing all Relavent Functions

class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0  # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j - 1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i - 1) or not self.cons(i - 2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]:  # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k - length + 1:self.k + 1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j + 1] + s + self.b[self.j + length + 1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):
                self.setto("ate")
            elif self.ends("bl"):
                self.setto("ble")
            elif self.ends("iz"):
                self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k + 1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):
                self.r("ate")
            elif self.ends("tional"):
                self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):
                self.r("ence")
            elif self.ends("anci"):
                self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):
                self.r("ble")  # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):
                self.r("al")
            elif self.ends("entli"):
                self.r("ent")
            elif self.ends("eli"):
                self.r("e")
            elif self.ends("ousli"):
                self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):
                self.r("ize")
            elif self.ends("ation"):
                self.r("ate")
            elif self.ends("ator"):
                self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):
                self.r("al")
            elif self.ends("iveness"):
                self.r("ive")
            elif self.ends("fulness"):
                self.r("ful")
            elif self.ends("ousness"):
                self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):
                self.r("al")
            elif self.ends("iviti"):
                self.r("ive")
            elif self.ends("biliti"):
                self.r("ble")
        elif self.b[self.k - 1] == 'g':  # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):
                self.r("ic")
            elif self.ends("ative"):
                self.r("")
            elif self.ends("alize"):
                self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):
                self.r("ic")
            elif self.ends("ful"):
                self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"):
                pass
            elif self.ends("ence"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"):
                pass
            elif self.ends("ible"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"):
                pass
            elif self.ends("ement"):
                pass
            elif self.ends("ment"):
                pass
            elif self.ends("ent"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'):
                pass
            elif self.ends("ou"):
                pass
            # takes care of -ous
            else:
                return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"):
                pass
            elif self.ends("iti"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"):
                pass
            else:
                return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"):
                pass
            else:
                return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k - 1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k - 1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b  # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k + 1]


# Function that calls Porter's Stemming Algorithm on the Corpus (Text files) generated from given PDf Data
def stemmingDataFiles() -> list[list[str]]:
    locationOfDataSet = "assets"
    accesingFolder = os.listdir(locationOfDataSet)

    p = PorterStemmer()
    # stores the name of the files
    nameOfDocuments = []
    # stores the list of strings where each string contains all the stemmed data of files.
    stemmedDocumentDataList = []

    for doc in accesingFolder:
        infile = open(fr"{locationOfDataSet}\\{doc}", 'r', encoding="utf8")
        nameOfDocuments.append(doc)
        output = ''
        while 1:
            word = ''
            line = infile.readline()
            if line == '':
                break
            for c in line:
                if c.isalpha():
                    word += c.lower()
                else:
                    if word:
                        output += p.stem(word, 0, len(word) - 1)
                        word = ''
                    output += c.lower()
        infile.close()
        stemmedDocumentDataList.append(output)
    return stemmedDocumentDataList, nameOfDocuments


# cleans the tokens and remove stop words from the vocabulary
def cleanData(unCleanDataList):
    # Stop list contains the words that are to be removed from the documents (These words are not requied to process the dataset and the user's query)
    stopList = list(string.ascii_lowercase)
    stopList.extend(('__', ';', ',', ':', '.', '(', ')', "’", '-', '“'))

    # It contains the words that are to be deleted from the list
    useLessWords = []

    # Running For loop on the data to remove stop words.
    for ind, listIitem in enumerate(unCleanDataList):
        if listIitem in stopList:
            useLessWords.append(listIitem)
        if listIitem[0] == '.':
            useLessWords.append(listIitem)
        elif "â€™" in listIitem:
            it = listIitem.replace("â€™", "'")
            unCleanDataList[ind] = it

    # new_list stores the cleaned data that is to be returned by this function
    new_list = [listIitem for listIitem in unCleanDataList if listIitem not in useLessWords]

    return new_list


# This is the function that tokenize the data using the NLTK word_tokenize function
def tokenizeFunction(stemmedDocList):
    tokensList = []
    for item in stemmedDocList:
        tokensList.append(word_tokenize(item))

    return tokensList


# getVocab function returns a set that contains all the unique terms of the corpus
def createVocab(tokenList):
    vocab = set()
    for item in tokenList:
        vocab.update(set(item))

    vocab = sorted(vocab)
    return vocab


# Fucntion that creates a Matrix that stores the frequency of each word in the given document.
# def findFrequencyOfEachWordInDocument(finalList, vocab):
#     frequencyOfWordInDocument = []
#     for list in finalList:
#         lisi = [0] * len(vocab)
#         for item in list[1]:
#             for i, it in enumerate(vocab):
#                 if item == it:
#                     lisi[i] += 1
#         frequencyOfWordInDocument.append(lisi)
#     return frequencyOfWordInDocument
# A 0-1 matix storing the frequency of each word in a document frequencyOfWordInDocument[i][j] => frequency of jth work in the ith docume
# Row contians the document number and column contains all the terms in the corpus
# frequencyOfWordInDocument[i][j] = 1 if ith document contains the jth word else frequencyOfWordInDocument[i][j] = 0
# frequencyOfWordInDocument = findFrequencyOfEachWordInDocument(finalList,vocab)


# Pre Processing the query
@functools.lru_cache(maxsize=None)
def queryProcessing(query):
    p = PorterStemmer()
    output = ''
    word = ''
    for c in query:
        if c.isalpha():
            word += c.lower()
        else:
            if word:
                output += p.stem(word, 0, len(word) - 1)
                word = ''
            output += c.lower()

    output = word_tokenize(output)
    output = cleanData(output)

    nl = []
    for word in output:
        word = word.strip()
        if '.' in word:
            nl += word.split('.')
        elif ',' in word:
            nl += word.split(',')
        else:
            nl.append(word)
    return nl


def getParagraphFromDocumnets():
    locationOfDataSet = "assets"
    accesingFolder = os.listdir(locationOfDataSet)

    paragraphs = []

    for doc in accesingFolder:
        with open(fr"{locationOfDataSet}\\{doc}", 'r', encoding="utf8") as filePtr:
            fileDataInString = filePtr.read()

        sentTokenizeDocList = sent_tokenize(fileDataInString)
        paragraph = []
        str = ""
        for i, it in enumerate(sentTokenizeDocList):
            if i % 15 == 0 and i != 0:
                paragraph.append(str)
                str = ''

            str += (it + ' ')

        if str != '':
            paragraph.append(str)
            str = ''

        paragraphs.append(paragraph)

    return paragraphs


def preProcessDataSet():
    stemmedDocumentDataList, nameOfDocuments = stemmingDataFiles()
    tokenizedList = tokenizeFunction(stemmedDocumentDataList)

    cleanDataTokensList = []

    for babyList in tokenizedList:
        newList = cleanData(babyList)
        cleanDataTokensList.append(newList)

    vocab = createVocab(cleanDataTokensList)
    paragraphs = getParagraphFromDocumnets()

    return vocab, paragraphs, nameOfDocuments


def creatingInvertedIndex(paragraphsList, vocab):
    invertedIndexMatrix = []
    for vocabItem in vocab:
        termOccurenceList = []
        for paragraphsOfGivenDocument in paragraphsList:
            dictParagraphOccurence = {}  # {Para : no of occu.}
            for j, paragraph in enumerate(paragraphsOfGivenDocument):  # (Para number, para data)
                pargraphTokens = queryProcessing(paragraph)  # tokens of para data
                countOccOfVocabItem = pargraphTokens.count(vocabItem)
                if countOccOfVocabItem != 0:
                    dictParagraphOccurence[f'Para {j}'] = countOccOfVocabItem
            termOccurenceList.append(dictParagraphOccurence)
        invertedIndexMatrix.append(termOccurenceList)
    return invertedIndexMatrix


def getQueryFromUser():
    # while 1:
    query = returnLastQuery()

    if query == '':
        print("No Query Found!")
        # continue
    else:
        print("The search results for query : ", query)

    phraseQuery = query
    query += ' '
    query = queryProcessing(query)

    return query, phraseQuery


def searchQuery(query, vocab, invertedIndexMatrix, nameOfDocuments):
    foundOccuInAllDocs = []

    for docNumber in range(len(nameOfDocuments)):
        flag = False
        dictQueryParaFreq = []

        for word in query:
            try:
                ind = vocab.index(word)
            except:
                flag = True
                break

            dictQueryParaFreq.append(invertedIndexMatrix[ind][docNumber])

        if flag:
            continue

        commonParasList = []
        num_words = len(query)

        for i in range(10000):
            count = 0
            for di in dictQueryParaFreq:
                try:
                    val = di[f"Para {i}"]
                    count += 1
                except:
                    pass

            if count == num_words:
                commonParasList.append(f"Para {i}")

        foundOccuInAllDocs.append(commonParasList)

    return foundOccuInAllDocs

def outputDataInStorageFile(foundOccuInAllDocsPhraseQuery, foundOccuInAllDocs, nameOfDocuments, paragraphs):
    # print("Phase Query Results: \n\n\n")

    filePtr = open('searchResultPhraseQuery.txt', 'w')
    for ind, doc in enumerate(foundOccuInAllDocsPhraseQuery):
        if doc:
            filePtr.write(f"Result Category: {nameOfDocuments[ind].split('_')[0]} Insurance\n")
            filePtr.write(f"Result found in File: {nameOfDocuments[ind]}\n")
            filePtr.write('\n')

            for item in doc:
                paraNumber = int(item[5:])
                filePtr.write(f'Paragraph {paraNumber}\n')
                filePtr.write(f'{paragraphs[ind][paraNumber]}\n')
                filePtr.write('\n')

            filePtr.write('\n\n')

    filePtr.close()

    filePtr = open('searchResultBoolean.txt', 'w')

    for ind, doc in enumerate(foundOccuInAllDocs):
        if doc:
            filePtr.write(f"Result Category: {nameOfDocuments[ind].split('_')[0]} Insurance\n")
            filePtr.write(f"Result found in File: {nameOfDocuments[ind]}\n")
            filePtr.write('\n')

            for item in doc:
                paraNumber = int(item[5:])
                filePtr.write(f'Paragraph {paraNumber}\n')
                filePtr.write(f'{paragraphs[ind][paraNumber]}\n')
                filePtr.write('\n')

            filePtr.write('\n\n')

    filePtr.close()

    # filePtr = open('searchResultBoolean.txt')
    # print(filePtr.read())
    # filePtr.close()
    return


def phaseQuery(phrase_query, foundOccuInAllDocsQuery, paragraphs):
    phaseQueryParaList = []

    for doc_num, paragraphList in enumerate(foundOccuInAllDocsQuery):
        phaseQueryParaList.append([])
        for paragraphIndex, para_number in enumerate(paragraphList):
            para = paragraphs[doc_num][int(para_number[5:])]
            if phrase_query.lower() in para.lower():
                phaseQueryParaList[-1].append(f"{para_number}")

    return phaseQueryParaList


if __name__ == "__main__":

    vocab, paragraphs, nameOfDocuments = preProcessDataSet()
    invertedIndexMatrix = creatingInvertedIndex(paragraphs, vocab)

    from UI import returnLastQuery, saveQueryListToFile

    # print(invertedIndexMatrix)
    # print(len(vocab))
    # print(len(invertedIndexMatrix))

    query, phraseQuery = getQueryFromUser()

    foundOccuInAllDocsQuery = searchQuery(query, vocab, invertedIndexMatrix, nameOfDocuments)
    foundOccuInAllDocsPhraseQuery = phaseQuery(phraseQuery, foundOccuInAllDocsQuery, paragraphs)

    # print(len(foundOccuInAllDocsQuery))
    outputDataInStorageFile(foundOccuInAllDocsPhraseQuery, foundOccuInAllDocsQuery, nameOfDocuments, paragraphs)

    saveQueryListToFile()





















# with open(r"assets\PROPERTY_147.txt", 'r', encoding="utf8") as fd:
#     fileDataInString = fd.read()
#
# # print(fileDataInString)
# tokenizeDocumnetInSentences = sent_tokenize(fileDataInString)
#
# paragraph = []
# str = ""
# for i, it in enumerate(tokenizeDocumnetInSentences):
#     if i % 15 == 0 and i != 0:
#         paragraph.append(str)
#         str = ''
#
#     str += (it + ' ')
#
# if str != '':
#     paragraph.append(str)
#     str = ''
#
#
# phrase_query = "we will pay"
#
# pqpl = []
#
# tc = 0
# for index, para in enumerate(paragraph):
#     if phrase_query.lower() in para.lower():
#         tc += para.lower().count(phrase_query.lower())
#         pqpl.append(f"para {index}")
#
# incMat, vocabDocument1 = creatingInvertedIndex(paragraph, fileDataInString)
#
# query = input("Enter the query: ")
# if query == '':
#     print("No Query Found!")
# else:
#     print("Your query is: ", query)
#
# query += ' '
#
# query = queryProcessing(query)
# print(query)
#
#
# def searchQuery(query, vocabDocument1: list, incMat):
#     if len(query) == 0:
#         print("No Query Found")
#         return
#
#     dl = []
#
#     for word in query:
#         try:
#             ind = vocabDocument1.index(word)
#         except:
#             print(f"{word} not found any document")
#             return
#             # raise ValueError
#
#         dl.append(incMat[ind])
#
#     common_paras_list = []
#     num_words = len(query)
#
#     for i in range(10000):
#         count = 0
#         for di in dl:
#             try:
#                 val = di[f"para {i}"]
#                 count += 1
#             except:
#                 pass
#         if count == num_words:
#             common_paras_list.append(f"para {i}")
#
#     return common_paras_list
#
#
# commonParagraphs = searchQuery(query, vocabDocument1, incMat)
# print(commonParagraphs)
#
# print(paragraph[43])
