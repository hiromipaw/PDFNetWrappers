#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2014 by PDFTron Systems Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------

import site
site.addsitedir("../../../PDFNetC/Lib")
import sys
from PDFNetPython import *

def printStyle (style):
    print(" style=\"font-family:" + style.GetFontName() + "; font-size:" 
          + str(style.GetFontSize()) + "; sans-serif: " + str(style.IsSerif()) 
          + "; color:" + str(style.GetColor())+ "\"")

def dumpAllText (reader):
    element = reader.Next()
    while element != None:
        type = element.GetType()
        if type == Element.e_text_begin:
            print("Text Block Begin")
        elif type == Element.e_text_end:
            print("Text Block End")
        elif type == Element.e_text:
            bbox = element.GetBBox()
            print("BBox: " + str(bbox.GetX1()) + ", " + str(bbox.GetY1()) + ", " 
                  + str(bbox.GetX2()) + ", " + str(bbox.GetY2()))
            textString = element.GetTextString()
            if sys.version_info.major >= 3:
                textString = ascii(textString)
            print(textString)
        elif type == Element.e_text_new_line:
            print("New Line")
        elif type == Element.e_form:
            reader.FormBegin()
            dumpAllText(reader)
            reader.End()
        element = reader.Next()

# A utility method used to extract all text content from
# a given selection rectangle. The recnagle coordinates are
# expressed in PDF user/page coordinate system.
def ReadTextFromRect (page, pos, reader):
    reader.Begin(page)
    srch_str = RectTextSearch(reader, pos)
    reader.End()
    return srch_str

#A helper method for ReadTextFromRect
def RectTextSearch (reader, pos):
    element = reader.Next()
    srch_str2 = ""
    while element != None:
        type = element.GetType()
        if type == Element.e_text:
            bbox = element.GetBBox()
            if (bbox.IntersectRect(bbox, pos)):
                arr = element.GetTextString()
                srch_str2 += arr
                srch_str2 += "\n"
        elif type == Element.e_text_new_line:
            None
        elif type == Element.e_form:
            reader.FormBegin()
            srch_str2 += RectTextSearch(reader, pos)
            print(srch_str2)
            reader.End()
        element = reader.Next()
    return srch_str2
            

def main():
    PDFNet.Initialize()
    
    # Relative path to the folder containing test files.
    input_path =  "../../TestFiles/newsletter.pdf"
    example1_basic = True
    example2_xml = True
    example3_wordlist = True
    example4_advanced = True
    example5_low_level = True
   
    # Sample code showing how to use high-level text extraction APIs.
    doc = PDFDoc(input_path)
    doc.InitSecurityHandler()
    
    page = doc.GetPage(1)
    if page == None:
        print("page no found")
        
    txt = TextExtractor()
    txt.Begin(page) # Read the page
    
    # Example 1. Get all text on the page in a single string.
    # Words will be separated witht space or new line characters.
    if example1_basic:
        print("Word count: " + str(txt.GetWordCount()))
        txtAsText = txt.GetAsText()
        if sys.version_info.major >= 3:
            txtAsText = ascii(txtAsText)
        print("- GetAsText --------------------------" + txtAsText)
        print("-----------------------------------------------------------")
   
    # Example 2. Get XML logical structure for the page.
    if example2_xml:
        text = txt.GetAsXML(TextExtractor.e_words_as_elements | 
                            TextExtractor.e_output_bbox | 
                            TextExtractor.e_output_style_info)       
        print("- GetAsXML  --------------------------" + text)
        
    print("-----------------------------------------------------------")
    
    # Example 3. Extract words one by one.
    if example3_wordlist:
        word = Word()
        line = txt.GetFirstLine()
        while line.IsValid():
            word = line.GetFirstWord()
            while word.IsValid():
                wordString = word.GetString()
                if sys.version_info.major >= 3:
                    wordString = ascii(wordString)
                print(wordString)
                word = word.GetNextWord()
            line = line.GetNextLine()
            
    print("-----------------------------------------------------------")
    print("Example 4")
    
    # Example 4. A more advanced text extraction example. 
    # The output is XML structure containing paragraphs, lines, words, 
    # as well as style and positioning information.
    if example4_advanced:
        bbox = Rect();
        cur_flow_id = -1
        cur_para_id = -1
        
        # For each line on the page...
        line = txt.GetFirstLine()
        while line.IsValid():
            if line.GetNumWords() == 0:
                continue
            word = line.GetFirstWord()
            if cur_flow_id != line.GetFlowID():
                if cur_flow_id != -1:
                    if cur_para_id != -1:
                        cur_para_id = -1;
                        print("</Para>")
                    print("</Flow>")
                cur_flow_id = line.GetFlowID()
                print("<Flow id=\"" + str(cur_flow_id) +"\">")
                    
            if cur_para_id != line.GetParagraphID():
                if cur_para_id != -1:
                    print("</Para>")
                cur_para_id= line.GetParagraphID()
                print("<Para id=\"" +str(cur_para_id)+ "\">")
                
            bbox = line.GetBBox()
            line_style = line.GetStyle()
            sys.stdout.write("<Line box=\"" + str(bbox.GetX1()) + ", " + str(bbox.GetY1()) + ", " + str(bbox.GetX2()) + ", " + str(bbox.GetY2()) + "\"")
            printStyle (line_style)
            sys.stdout.write(">")
            
            # For each word in the line...
            word = line.GetFirstWord()
            while word.IsValid():
                # Output the bounding box for the word
                bbox = word.GetBBox()
                sys.stdout.write("<Word box=\"" + str(bbox.GetX1()) + ", " + str(bbox.GetY1()) + ", " + str(bbox.GetX2()) + ", " + str(bbox.GetY2()) + "\"")
                
                sz = word.GetStringLen()
                if sz == 0:
                    continue
                # If the word style is different from the parent style, output the new style.
                s = word.GetStyle()
                if s != line_style:
                    printStyle (s);
                wordString = word.GetString()
                if sys.version_info.major >= 3:
                    wordString = ascii(wordString)
                sys.stdout.write(">" + wordString + "</Word>\n")
                word = word.GetNextWord()                
            line = line.GetNextLine()
            
        if cur_flow_id != -1:
            if cur_para_id != -1:
                cur_para_id = -1
                sys.stdout.write("</Para>\n")
            sys.stdout.write("</Flow>\n")
        
        txt.Destroy()
        doc.Close()            
        print("Done.")
    
    # Sample code showing how to use low-level text extraction APIs.
    if example5_low_level:
        doc = PDFDoc(input_path)
        doc.InitSecurityHandler()

        # Example 1. Extract all text content from the document
        
        reader = ElementReader()
        itr = doc.GetPageIterator()
        while itr.HasNext():
            reader.Begin(itr.Current())
            dumpAllText(reader)
            reader.End()
            itr.Next()
            
        # Example 2. Extract text content based on the 
        # selection rectangle.
        
        print("----------------------------------------------------")
        print("Extract text based on the selection rectangle.")
        print("----------------------------------------------------")
        
        itr = doc.GetPageIterator()
        first_page = itr.Current()
        s1 = ReadTextFromRect(first_page, Rect(27, 392, 563, 534), reader)
        if sys.version_info.major >= 3:
            s1 = ascii(s1)
        print("Field 1: " + s1)

        s1 = ReadTextFromRect(first_page, Rect(28, 551, 106, 623), reader);
        if sys.version_info.major >= 3:
            s1 = ascii(s1)
        print("Field 2: " + s1)

        s1 = ReadTextFromRect(first_page, Rect(208, 550, 387, 621), reader);
        if sys.version_info.major >= 3:
            s1 = ascii(s1)
        print("Field 3: " + s1)
        
        doc.Close()
        print("Done.")
        
if __name__ == '__main__':
    main()
              