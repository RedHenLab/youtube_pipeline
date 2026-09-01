import sys, re
from somajo import SoMaJo

def add_10ms(timestamp):
    # Plain seconds arithmetic instead of datetime() -- datetime's hour field
    # is capped at 23, but long VTT files (multi-hour streams/lectures) can
    # have timestamps at or past 24:00:00.
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(".")
    total_ms = ((int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)) + 10
    h, rem_ms = divmod(total_ms, 3600000)
    m, rem_ms = divmod(rem_ms, 60000)
    s, ms = divmod(rem_ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

# We have 3-line blocks, and the new stuff can always be found in the last line, so we can probably ignore the secoond one.
# ToDo: There are 10 msec pauses because of the line feeds. We should try to find out which way they are more likely.
# ToDo: We may be able to use statistics for this (i.e. compare the average length of certain words at the beginning of sentence vs. somewhere else)
# For now they will be added to the last word of the previous line. We can always change this if it causes trouble.

openctags = 0
wordcounter = 1

tokenizer = SoMaJo("en_PTB", split_camel_case=False, split_sentences=False)
def tokenize_word (intext):
    return(tokenizer.tokenize_text(intext))


with open(sys.argv[1], encoding="utf-8") as infile:
    for line in infile:
        line = line.strip()
        match1 = re.match("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]) --> ([0-9][0-9]):([0-9][0-9]):([0-9][0-9]).([0-9][0-9][0-9])", line)
        if match1:
            # This is the first line of the triplet
            currenttime = match1.group(1)
            endtime = add_10ms(f"{match1.group(2)}:{match1.group(3)}:{match1.group(4)}.{match1.group(5)}")
            next(infile) # This is the second line. We are never interested in the second line.
            thirdline = next(infile)
            thirdline = thirdline.strip()
            if thirdline == "":
                continue
            match2 = re.search("<c", thirdline)
            # We are going to use a very simple approach here to detect boundaries: We replace all possible boundaries with Pipes.
            # In case there are real pipes, let us replace them first:
            thirdline = re.sub("\|", "__IAMAPIPE__", thirdline)
            thirdline = re.sub("<", "|<", thirdline)
            thirdline = re.sub(">", ">|", thirdline)
            thirdline = re.sub(" *\|[| ]*", "|", thirdline)
            thirdline = re.sub("^\|", "", thirdline)
            thirdline = re.sub("\|$", "", thirdline)
            items = thirdline.split("|")
            color = "default"
            word = ""
            for item in items:
                match3 = re.match("<c.color(.{6})", item)
                if match3:
                    color = match3.group(1)
                    openctags += 1
                    continue
                match4 = re.match("<c>", item)
                if match4:
                    openctags += 1
                    continue
                match5 = re.match("<([0-9].*?)>", item)
                if match5:
                    newtime = match5.group(1)
                    if word != "":
                        chunks = tokenize_word([word])
                        for chunk in chunks:
                            for token in chunk:
                                if not re.match("[\.,\!\?]+", token.text):
                                    print(wordcounter, "\t", token.text, "\t", "_\t" * 7, currenttime + "__" + newtime + "__" + color, sep="")
                                    wordcounter += 1
                        word = ""
                    currenttime = newtime
                    continue
                match6 = re.match("</c>", item)
                if match6:
                    openctags -= 1
                    if openctags == 0:
                        color = "default"
                    continue
                # If we got till here, we must have the word...
                word = re.sub("__IAMAPIPE__", "|", item.strip())
            if word != "":
                chunks = tokenize_word([word])
                for chunk in chunks:
                    for token in chunk:
                        if not re.match("[\.,\!\?]+", token.text):
                            print(wordcounter, "\t", token.text, "\t", "_\t" * 7, currenttime + "__" + endtime + "__" + color, sep="")
                            wordcounter += 1
