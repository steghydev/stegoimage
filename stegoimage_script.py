'''
@author: Simone Gentili
'''
from operator import truediv
import sys as s
from imgPackage import images
from PIL import Image
import os



usage = "python stegoz.py [option] ... [files] ...\n"\
        "To encode: --encode [text] or [path_to_file] [path_to_image] [destination_path]\n"\
        "To decode: --decode [path_to_img]\n"\
        "To comapare: --compare [source_path1] [source_path2] [destination_path]\n"\
        "IMPORTANT: In any case, the images must have a png extension.\n"\
        "visit my Git at : https://github.com/GentiliSimone for other fun stuff."

signature = 'stegofile'

# =============================================================================
#  Text to binary
# =============================================================================

def toBinary(num,length):

    '''
        Converts the specified number to base 2 using the specified
        length to represent it. Returns the binary sequence obtained.
        If the number is not representable with the specified length
        binary sequence, the method throws a ValueError.
    '''
    num = bin(num)
    if len(num[2:])>length:
        raise Exception("Cannot extends the specified num")
    newNum = "0b"
    for i in range(0,length-len(num[2:])):
        newNum += '0'
    newNum += num[2:]
    return newNum

def genEncodings():

    '''
        Returns a dictionary containing the associations between
        characters and binary sequences.
    '''
    alphabetic  = 'qwertyuiopèéasdfghjklòàùzxcvbnm'
    numbers = '0123456789'
    simbols = '\ !"$%\'/()=?[{*}]@,.:-_'
    length = 6
    encodings = dict()
    i = 0
    for c in alphabetic:
        encodings[c] = toBinary(i,length)
        i += 1
    for c in numbers:
        encodings[c] = toBinary(i,length)
        i += 1
    for c in simbols:
        encodings[c] = toBinary(i,length)
        i += 1
    return encodings

encodedSequences = genEncodings() #dictionary for encodings
decodedSequences = {encodedSequences[k]:k for k in encodedSequences} #dictionary for deconding

def getBinaryWord(word):

    '''
        Converts the specified literal sequence to a list containing
        the binary sequences of each character in the string.
        If the specified word is "ciao" the result is:
        [('011010'),('000111'),('001100'),('001000')]
    '''
    if not isinstance(word,str):
        raise ValueError("The specified word is not a str object")
    binaryWord = list()
    for char in word:
        if not char in encodedSequences:
            binaryWord.append(encodedSequences[" "])
        else:
            binaryWord.append(encodedSequences[char])
    return binaryWord

def splitSequence(sequence):

    '''
        Returns a tuple containing the binary subsequences of the
        specified binary sequence (each sub-sequence has a length
        equal to 2). If the specified sequence is not a binary
        sequence, the method throws a ValueError.
        The binary String "0b010011" becomes:
                        ('01', '00', '11')
    '''

    if sequence[1] != 'b' or len(sequence[2:])%2 != 0:
        raise Exception("cannot divide this string: ",sequence)
    splitWord = list()
    s = 2
    e = 4
    for i in range(len(sequence[2:])//2):
        splitWord.append(sequence[s:e])
        s += 2
        e += 2
    return tuple(splitWord)

def getSubSequencesOf(word):

    '''
        Returns a list containing a certain number of tuples.
        The i-th tuple contained in the list contains the subsequences
        of length 2 of the binary sequence associated with the i-th
        character of the specified word.
           The string "ciao" becomes:
             (('01', '10', '10'),
              ('00', '01', '11'),
              ('00', '11', '00'),
              ('00', '10', '00'))
    '''

    splittedBinaryWord = list()
    try:
        binaryWord = getBinaryWord(word)
    except ValueError as v:
        return tuple([('10','10','10') for i in range(len(word))])
    for sequence in binaryWord:
        subSequence = splitSequence(sequence)
        splittedBinaryWord.append(subSequence)
    return splittedBinaryWord

# =============================================================================
#   Encode
# =============================================================================

def getCoordinate(img, line, column, k):

    '''
        Increments the specified (line, column) coordinates with the
        k value and returns the new coordinates obtained.
    '''

    column += k
    while( column >= len(img[0]) ):
        line += 1
        column -= len(img[0])
    return line, column

def writeSubWord(char,pixel):
    '''
        Returns a tuple containing three values ​​obtained by embedding
        the specified character (intended binary sequence) within the
        specified pixel using the LSB method.
        _____________________________________________________________
        EXAMPLE:

         input = char('01','10','10'), pixel(255,0,128)

                 01 ----> 111111(01) ----> 253  |\
            char 10 ----> 000000(10) ----> 2    | > (253, 2, 130)
                 10 ----> 100000(10) ----> 130  |/

        output = (253, 2, 130)
    '''
    if not isinstance(pixel, tuple) or len(pixel) != 3:
        raise ValueError("The specified pixel is not valid: ", pixel)
    if not isinstance(char, tuple) or len(char) != 3:
        raise ValueError("Invalid encoding for the specified char:", char)
    pixel = list(pixel)
    for i in range(3):
        binaryChannel = toBinary(pixel[i], 8)
        print(" | ", binaryChannel, " | --> ",end='')
        newBinaryChannel = binaryChannel[:8] + char[i]
        print(" | ", newBinaryChannel, " |")
        pixel[i] = int(newBinaryChannel, 2)
    print( "")
    return tuple(pixel)

def write(word,img,y,x,k):

    '''
       Writes the specified word into the specified image at the specified
       coordinates leaving k pixels unchanged whenever a character is embedded.
    '''

    length = len(word)
    encodedWord = getSubSequencesOf(word)
    indexChar = 0
    count = 0
    coordinates = list()
    for line in range(y,len(img)):
        for column in range(x,len(img[line])):
            if indexChar == length:
                return getCoordinate(img, line, column-1, k), tuple(coordinates)
            if count == k:
                count = 0
            if count == 0:
                img[line][column] = writeSubWord(encodedWord[indexChar],img[line][column])
                indexChar += 1
            count += 1
            if indexChar == length:
                coordinates.append(line)
                coordinates.append(column)
        x = 0


def writeText(text,img,k,y,x,i):

    '''
        Embed the specified text within the specified image starting at the specified
        coordinates. The characters contained in the specified text are embedded every
        k pixel in the image.
    '''

    word = text[i:i+1][0]
    coordinates = write(word,img,y,x, k)
    if not text[i+1:]:
        writeInformations(coordinates[1][0], coordinates[1][1], img, k)
        return
    writeText(text,img,k,coordinates[0][0], coordinates[0][1], i+1)

def writeInformations(y,x,img,k):

    '''
        Writes the information needed for decoding. From coordinates
        0,0 to coordinates 0,8 it writes the signature of the file.
        From coordinates 0,9 to coordinates 0,12 it writes the coordinates
        that determine the position of the last character written in the
        coding phase. From coordinates 0,13 to coordinates 0,16 it writes
        the step (i.e. the integer value that determines how often a single
        character has been incorporated into a pixel in the image).
    '''

    binarySignature = getSubSequencesOf(signature)
    for i in range(9):
        img[0][i] = writeSubWord(binarySignature[i], img[0][i])
    binaryCoordinateY = splitSequence(toBinary(y, 12))
    img[0][9] = writeSubWord(binaryCoordinateY[0:3], img[0][9])
    img[0][10] = writeSubWord(binaryCoordinateY[3:], img[0][10])
    binaryCoordinateX = splitSequence(toBinary(x, 12))
    img[0][11] = writeSubWord(binaryCoordinateX[0:3], img[0][11])
    img[0][12] = writeSubWord(binaryCoordinateX[3:], img[0][12])
    binaryStep = splitSequence(toBinary(k, 24))
    img[0][13] = writeSubWord(binaryStep[0:3], img[0][13])
    img[0][14] = writeSubWord(binaryStep[3:6], img[0][14])
    img[0][15] = writeSubWord(binaryStep[6:9], img[0][15])
    img[0][16] = writeSubWord(binaryStep[9:12], img[0][16])

def checkValidityEncode(img, text):

    '''
        Checks if the specified image is too large (greater than 4095x4095) ,
        or if it's too small for the specified text (the width must be at
        least 17 pixels).
        If one of the cases indicated occurs, the method throws a ValueError
        exception.
    '''

    if not len(img)*len(img[0])-17 >= len(text) or len(img[0]) < 17:
        raise ValueError("The image is too small for the specified text")
    if len(img) > 4095 or len(img[0]) > 4095:
        raise ValueError("The image is too big")

def getText(text):

    '''
        Reads the content of the specified text (if it is a file it opens
        it in reading mode) and returns two elements: a list containing the
        words of the text in which each word contains a space in the last
        position (with the exception of the last element of the list ) and
        the unaltered text in string format.
    '''

    if os.path.isfile(text):
        with open(text,mode = "r") as file:
            text = file.read()
    textList = [s+' ' for s in text.lower().split()]
    textList[-1] = textList[-1][:-1] #tolgo lo spazio all'ultimo carattere
    return textList, text

def encode(textPath, sourceImg, destImg):

    '''
        Main method for embedding the specified text within the specified
        source image. The source image is not modified but only used as a
        template to embed the text. The image containing the embedded text
        is saved in the specified path.
        In order, the operations performed by the method are:
        1) capture of the text file.
        2) capture of the image matrix.
        3) Analysis of the validity of the matrix.
        4) Determination of the step to embed fonts.
        5) Incorporation of the characters inside the image.
        6) Saving of the obtained matrix within the specified path.
    '''

    text = getText(textPath)
    img = images.load(sourceImg)
    checkValidityEncode(img, text[1])
    k = (len(img)*len(img[0]) - 17) // len(text[1])
    writeText(text[0],img,k,0,17,0)
    images.save(img, destImg)

# =============================================================================
#  Decode
# =============================================================================

def checkValidityDecode(img):

    '''
       It analyzes the specified matrix and determines if it contains the
       signature and if the width of the matrix is ​​sufficient to contain it.
       If the width is not sufficient, or if the array is too large (greater
       than 4095 x 4095) or does not contain the signature, the method throws a
       ValueError exception.
    '''

    tempString = ''
    if len(img[0]) < 17:
        raise ValueError("the specified image is not valid. Width < 13")
    if len(img) > 4095 or len(img[0]) > 4095:
        raise ValueError("The specified image is to large")
    for pixel in img[0][0:9]:
        tempString += decodeBinarySequence(decodePixel(pixel))
    if tempString != signature:
        raise ValueError("The specified image is not valid")

def decodePixel(pixel):

    '''
        Returns the binary sequence obtained from the LSBs of the bytes of
        the specified pixel.
        If the pixel is (255,128,0):

              R  255 ----> 111111(11) ----> 11  |\
        pixel G  128 ----> 100000(00) ----> 00  | > 110000
              B  0   ----> 100000(00) ----> 00  |/
    '''

    binaryChar = '0b'
    for channel in pixel:
        binaryChar += toBinary(channel,8)[8:]
    return binaryChar

def getInformations(img):

    '''
        It takes from the image the information necessary for the decoding
        of the characters. the information is collected in accordance with
        the function that inserts this information into the image.
    '''

    tempY = decodePixel(img[0][9]), decodePixel(img[0][10])
    tempX = decodePixel(img[0][11]),decodePixel(img[0][12])
    tempK = decodePixel(img[0][13]),decodePixel(img[0][14]), \
            decodePixel(img[0][15]),decodePixel(img[0][16])
    y = tempY[0] + tempY[1][2:]
    x = tempX[0] + tempX[1][2:]
    k = tempK[0] + tempK[1][2:] + tempK[2][2:] + tempK[3][2:]
    return int(y, 2), int(x, 2), int(k, 2)

def decodeBinarySequence(sequence):

    '''
        Decodes the specified binary sequence using the decoding dictionary and
        returns the obtained value. If the specified binary sequence is not
        registered in the decoding dictionary, the method throws a ValueError
        exception (In particular, it happens when the specified binary sequence
        is made up of more than 6 bits or less than 6 bits).
    '''

    if sequence in decodedSequences:
        return decodedSequences[sequence]
    else:
        raise ValueError('Cannot decode the sequence: ',sequence)

def decode(imgPath):

    '''
        If the specified image is valid for decoding (it has been modified using
        this script) returns the text embedded within this image.
    '''

    img = images.load(imgPath)
    checkValidityDecode(img)
    y, x, k = getInformations(img)
    clearText = ""
    start = 17
    coordinates = (0, 17)
    for l in range(0,len(img)):
        if(l != 0):
            start = 0
        for c in range(start,len(img[l])):
            if l == coordinates[0] and c == coordinates[1]:
                decodedChar = decodeBinarySequence(decodePixel(img[l][c]))
                clearText += decodedChar
                if coordinates[0] == y and coordinates[1] == x:
                    break
                coordinates = getCoordinate(img, l, c, k)
    return clearText

# =============================================================================
#  Analyzer
# =============================================================================

def getComparativeImage(pathImg1, pathImg2, destination):

    '''
        Compare the two specified images. If the two images have different widths
        or different lengths, the method throws a ValueError exception. Otherwise,
        if the two images have the same size, it compares each pixel of the first
        image with the corresponding pixel in the second image and writes a red pixel
        in a new image at that point if the two pixels are different.
        The new image obtained by comparing the two images is saved in the specified path.
    '''

    img1 = images.load(pathImg1)
    img2 = images.load(pathImg2)
    count = 0
    if len(img1) != len(img2) or len(img1[0]) != len(img2[0]):
        raise ValueError("incompatible images")
    img = [[(0,0,0) for c in range(len(img1[0]))] for l in range(len(img1))]
    for y in range(len(img1)):
        for x in range(len(img1[0])):
            if img1[y][x] != img2[y][x]:
                count += 1
                img[y][x] = (255,0,0)
    images.save(img, destination)
    print(" ")
    print("Different pixels detected: ", count)    
    Image.open(destination).show()


#################################################################################
""" """
#################################################################################

if __name__=='__main__':
    if(s.argv[1:]):
        if(s.argv[1]=='--encode'):
            try:
                encode(s.argv[2], s.argv[3], s.argv[4])
            except ValueError as v:
                print(v.args)
        elif(s.argv[1]=='--decode'):
            try:
                print(" ")
                print(decode(s.argv[2]))
            except ValueError as v:
                print(v.args)
        elif(s.argv[1]=='--compare'):
            try:
                getComparativeImage(s.argv[2], s.argv[3], s.argv[4])
            except ValueError as v:
                print(v.args)
        else:
            print(usage)
    else:
        print(usage)
