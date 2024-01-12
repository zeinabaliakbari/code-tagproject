# -*- coding: utf-8 -*-

import re

def convertProfile(srcFile, dstFile):    
    
    #privateDict = r'D:\dev\ProstateAnalysis\tools\Siemens_BDO_DICOM_anonymizer_2.4_MR\CTP\Our_PrivateTagDictionary_v2.xml'
    privateDict = r'emptyFile.txt'        
    
    keepOnlyEnabled = True
    
    #expr = re.compile('\s*<(?:[ekr]) en="(?P<Enabled>[TF])" t="(?P<TagID>[0-9a-zA-Z]+)"[\s]?(?:n="(?P<Name>[\sa-zA-Z0-9]*)")?>(?P<Action>.*)</(?:[ekr]>)')
    expr = re.compile('\s*<(?:[e]) en="(?P<Enabled>[TF])" t="(?P<TagID>[\w\s\[\]]+)"[\s]?(?:n="(?P<Name>[\w\s_\-\,\.\/\#\(\)]*)")?>(?P<Action>.*)</(?:[ekr]>)')
    
    rules = []
    with open(srcFile, 'r') as fid:
        ctpProfile = fid.readlines()
        
        for l in ctpProfile:
            m = re.match(expr, l)
            if m is None:
                
                
                
                print("Warning: unable to parse line: " + l)
            else:
                rules.append(m.groupdict())

    # split tag ID into groups and element
    for r in rules:
        m = re.match(re.compile("(?P<Group>[0-9a-fA-F]{4})(\[(?P<PrivateCreator>[\w\s]+)\])?(?P<Elem>[0-9a-fA-F]{2,4})?"), r["TagID"])
        if m is not None:
            d = m.groupdict()
            if "Group" in d:
                r["Group"] = d["Group"]
            if "Elem" in d:
                r["Elem"] = d["Elem"]
            if "PrivateCreator" in d:
                r["PrivateCreator"] = d["PrivateCreator"]
                


    privExpr = re.compile('\s*<element code="K" cr="(?P<PrivateCreator>[\w\s]+)" gp="(?P<Group>[0-9a-fA-F]+)" el="(?P<Elem>[0-9a-fA-F]+)" src="(?P<Name>[\w\s_\-\,\.\/\#\(\)]+)"/>')
    privRules = []
    with open(privateDict, 'r') as fid:
        priv = fid.readlines()
        
        for l in priv:
            m = re.match(privExpr, l)
            if m is None:
                print("Warning: unable to parse line: " + l)
            else:
                d = m.groupdict()
                d["Enabled"] = "T"
                d["Action"] = "@keep()"
                d["Source"] = srcFile
                privRules.append(d)
    
    with open(dstFile, 'w+') as fid:
       # fid.write("sep=;\n")
        #cols = ["Enabled", "Group", "Elem", "PrivateCreator", "Name", "Action"]
        cols = ["Group", "PrivateCreator", "Elem",  "Name", "Action"]
        fid.write(";".join(cols) + "\n")
        for r in rules:
            r["Source"] = srcFile
            if keepOnlyEnabled == True and r["Enabled"] == "T" and not (r["Action"] == ""):
                outLine = ""
                for c in cols:
                    outLine = outLine + ((r[c] if c in r and r[c] is not None else "") + ";")
                # remove last semicolon
                outLine = outLine[:-1] + "\n"
                fid.write(outLine)
            
        for r in privRules:
            if keepOnlyEnabled == True and r["Enabled"] == "T" and not (r["Action"] == ""):
                outLine = ""
                for c in cols:
                    outLine = outLine + ((r[c] if c in r and r[c] is not None else "") + ";")
                outLine = outLine[:-1] + "\n"
                fid.write(outLine)
                    
        

if __name__ == "__main__":
    srcFile = r'DicomAnonymizer_Whitelist.script'
    dstFile = r'Profile1.csv'
    convertProfile(srcFile, dstFile)
 
    
    
