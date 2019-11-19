'''
TO DO:
    * Create 2 more PredicateObject Templates: Constant
    * Implement the functions SpreadSheet
    * Dockerize
'''

import pandas
import sys
import os
import shutil
import go_template
import json
import argparse

tmpDir = '../tmp/'
templatesDir = '../templates/'
resultDir = '../result/'
supportedLanguages = {'rml', 'r2rml', 'yarrrml'}

def checkFile(path):
    try:
        data = pandas.ExcelFile(path)
        return True
    except:
        print("Algo salio mal")
        return False

def generateJson(path):
    data = pandas.ExcelFile(path)
    json = {}
    for sheet_ in data.sheet_names:
        sheet = str(sheet_)
        json[sheet] = {}
        json[sheet] = generateJsonCols(data.parse(sheet))
    return json

def generateJsonCols(data):
        rng = len(data[data.columns[0]])
        result = []
        for row in range(0, rng):
            element = {}
            for col_ in data.columns:
                col = str(col_)
                element[col] = str(data[col][row])
            result.append(element)
        return result
def organizeJson(data):
    json = {}
    json['Prefixes'] = data['Prefixes']
    json['TriplesMap'] = {}
    for subject in data['Subject']:
        json['TriplesMap'][subject['ID']] = findChilds(data, subject['ID']) 
        json['TriplesMap'][subject['ID']]['Subject'] = subject
        json['TriplesMap'][subject['ID']]['Subject']['SubjectType'] = predicateTypeIdentifier(subject['URI'])
        json['TriplesMap'][subject['ID']]['Source'] = reFormatSource(json['TriplesMap'][subject['ID']]['Source'])
        json['TriplesMap'][subject['ID']]['PredicateObjectMaps']  =  reFormatPredicateObject(json['TriplesMap'][subject['ID']]['PredicateObjectMaps']) 
    return json

def replaceVars(element, type_):
    config = json.loads(open(templatesDir + 'config.json').read())
    if(type_ != 'constant' and str(config['variable'][type_]['before']) != '{' and str(config['variable'][type_]['after']) != '}'):
        result = element.replace("{", str(config['variable'][type_]['before'])).replace("}", config['variable'][type_]['after'])
    else:
        result = element
#    print(str(data) + ":" + str(result))
    return result
            
def findChilds(data, ID):
    result = {}
    keys = sorted(data.keys())
    keys.remove('Subject')
    keys.remove('Prefixes')
    keys.remove('Functions')
    for key in keys:
        result[key] =  []
        for element in data[key]:
#           print("New Element: ")
#           print(element)
            if(element['ID'] == ID):
                result[key].append(element)
    return result


def reFormatPredicateObject(data):
    result = {'Join':[], 'Template':[], 'Function':[], 'ReferenceObject':[], 'ConstantObject':[]}
    nullValues =  {'', 'NaN', ' ', 'nan', 'NAN'} 
    for element in data:
        element['PredicateType'] = predicateTypeIdentifier(element['Predicate'])
        if(str(element['Object'])in nullValues and str(element['InnerRef']) not in nullValues and str(element['OuterRef']) not in nullValues):
            element['TermType'] = termTypeIdentifier(element['Object'])
            element['ObjectType'] = 'reference'
            result['Join'].append(element)
        elif(str(element['Object'])[:1] == '<' and str(element['Object'])[-1:] == '>'):
            element['TermType'] = termTypeIdentifier(element['Object'])
            element['ObjectType'] = 'reference' 
            result['Function'].append(element)
        elif(len(str(element['Object']).split(" ")) > 1):
            element['TermType'] = termTypeIdentifier(element['Object'])
            element['ObjectType'] = 'template'
            result['Template'].append(element)
        elif(str(element['Object'])[:1] != '{' and str(element['Object'])[-1:] != '}' ):
            element['TermType'] = termTypeIdentifier(element['Object'])
            element['ObjectType'] = 'constant' 
            #element['Object'] = str(element['Object'])[1:-1]
            result['ConstantObject'].append(element)
        else:
            element['TermType'] = termTypeIdentifier(element['Object'])
            element['ObjectType'] = 'reference' 
            #element['Object'] = str(element['Object'])[1:-1]
            result['ReferenceObject'].append(element)
           #print(element['Object'])
    return result
def termTypeIdentifier(element):
    if(len(str(element).split(":")) == 2):
        return 'IRI'
    else: 
        return 'literal'
        
def predicateTypeIdentifier(element):
    if(len(str(element).split(":")) == 2 and "{" not in str(element) and "}" not in str(element)):
        return 'constant'
    elif(str(element)[:1] == '{' and str(element)[-1:] == '}' and str(element).split(" ")  == 1):
        return 'reference'
    elif(len(str(element).split(" ")) > 1 or len(str(element).split(":")) == 2 and "{" in str(element) and "}" in str(element)):
        return 'template'
    else:
        print("¡¡Revisa TermpredicateTypeIdentifier!!")
        sys.exit()
 
def reFormatSource(data):
    result = {}
    for element in data:
        if(element['Feature'] == 'source'):
            result['Source'] = str(element['Value']).lower()
        elif(element['Feature'] == 'format'):
            result['Format'] = str(element['Value']).lower()
        elif(element['Feature'] == 'iterator'):
            result['Iterator'] = str(element['Value']).lower()
        elif(element['Feature'] == 'table'):
            result['Source'] = str(element['Value']).lower()
    if('Iterator' not in result.keys()):
            result['Iterator'] = ''
    result['ID'] = data[0]['ID']
    return result

def writeValues(data, path):
    writePrefix(data,path)
    #data.remove('Prefixes')
    #f = open('result.txt', 'a+')
    for triplesmap in data['TriplesMap']:
        writeTriplesMap(triplesmap, path)
        writeSubject(data['TriplesMap'][triplesmap]['Subject'], path)
        writeSource(data['TriplesMap'][triplesmap]['Source'], path)       
        writePredicateObjects(data['TriplesMap'][triplesmap]['PredicateObjectMaps'], path)

def writePrefix(data, path):
    for prefix in data['Prefixes']:
        f = open(path + 'Prefixes.yml', 'a+')
        for element in prefix:
            f.write(str(element) + ': ' + str(prefix[element]) + '\n')
        f.close()
        go_template.render_template(templatesDir + 'Prefixes.tmpl',tmpDir + 'Prefixes.yml', tmpDir + 'Prefixes.txt')
        writeResult('', 'Prefixes')

def writeTriplesMap(data, path):
    f = open(path + 'TriplesMap.yml', 'a+')
    f.write('ID: ' + str(data) + '\n')
    f.close()
    go_template.render_template(templatesDir + 'TriplesMap.tmpl',tmpDir + 'TriplesMap.yml', tmpDir + 'TriplesMap.txt')
    writeResult(str(data), 'TriplesMap')

def writePredicateObjects(data, path):
   # print(data)
    for key in data:
        if(len(data[key]) > 0):
            for predicateObjects in data[key]:
                f = open(path + key + '.yml', 'a+')
                predicateObjects['Object'] = replaceVars(str(predicateObjects['Object']), str(predicateObjects['ObjectType']))
                predicateObjects['Predicate'] = replaceVars(str(predicateObjects['Predicate']), str(predicateObjects['PredicateType']))
                if( 'InnerRef' in predicateObjects.keys() and 'OuterRef' in predicateObjects.keys()):
                    predicateObjects['InnerRef'] = replaceVars(str(predicateObjects['InnerRef']), 'template')
                    predicateObjects['OuterRef'] = replaceVars(str(predicateObjects['OuterRef']), 'template')

                for element in predicateObjects:
                    #print(str(element) + ': ' + str(value) + '\n')
                    f.write(str(element) + ': \'' + predicateObjects[element] + '\'\n')
                f.close()
                go_template.render_template(templatesDir + key + '.tmpl',tmpDir + key + '.yml', tmpDir + key + '.txt')
                writeResult(data[key][0]['ID'], key)
            #print("Key: " + key + " ID: " + data[key][0]['ID'])

def writeSource(data, path):
    f = open(path + 'Source.yml', 'a+')
    config  = json.loads(open(templatesDir + 'config.json').read())
    if(data['Iterator'] != ''):
        data['Iterator'] = str(config['iterator']['before']) + str(data['Iterator']) + str(config['iterator']['after'])
    for element in data:
#        value = replaceVars(data[element])
        f.write(str(element) + ': \'' + data[element] + '\'\n')
    f.close()
    go_template.render_template(templatesDir + 'Source.tmpl',tmpDir + 'Source.yml', tmpDir + 'Source.txt')
    writeResult(data['ID'], 'Source')

   
def writeSubject(data, path):
    f = open(path + 'Subject.yml', 'a+')
    data['URI'] = replaceVars(data['URI'], data['SubjectType'])
    for element in data:
        f.write(element + ': ' + data[element] + '\n')
    f.close()
    go_template.render_template(templatesDir + 'Subject.tmpl',tmpDir + 'Subject.yml', tmpDir + 'Subject.txt')
    writeResult(data['ID'], 'Subject')

def writeResult(ID, name):
    delete = open(tmpDir + name + '.txt', 'r')
    final = open(resultDir + ID + '.' + name + '.' + 'result.txt', 'a+')
    final.writelines(delete.readlines())
    delete.close()
    final.close()
    try:
        os.remove(tmpDir + name + '.txt')
        os.remove(tmpDir + name + '.yml')
    except:
        pass

def writeFinalFile(path_, idList):
    data = json.loads(open(templatesDir  + 'structure.json').read())
    config = json.loads(open(templatesDir + 'config.json').read())
    path = path_ + '.' +  str(config['extension'])
    recursiveWrite(0,data['unique'], path, '')
    for id_ in idList:
        recursiveWrite(0,data['variable'], path, id_)

def recursiveWrite(tabs, parent, finalFile, id_):
    for data in range(0, len(parent)):
        file_ = resultDir + id_ + '.' + parent[data]['file'] + '.result.txt'
        config = json.loads(open(templatesDir + 'config.json').read())
        #print(file_)
        exists = os.path.isfile(file_)
        if(exists):
            f = open(file_, 'r')    
            final = open(finalFile, 'a+')
            if(str(parent[data]["before"]) != ""):
                final.write(parent[data]["before"] + '\n')
            for line in f.readlines():
                final.write(' ' * int(config['tab']['size']) * tabs + str(line))
            f.close()
            os.remove(file_)
            final.close()
            if(len(parent[data]['childs']) > 0):
                recursiveWrite(parent[data]['tabs'], parent[data]['childs'], finalFile, id_)
            if(str(parent[data]["after"]) != ""):
                final = open(finalFile, 'a+')
                final.write(parent[data]["after"] + '\n')
                final.close()
def cleanDir(path):
    Dir = os.listdir(path)
    for f in Dir:
        os.remove(path + f)
def generateMapping(inputFile):
    cleanDir("../result/")
    json = generateJson(inputFile)
    # print("First JSON: ")
    # print(str(json).replace('\'', '\"'))
    json = organizeJson(json)
    #print("Second JSON: ")
    #print(str(json).replace('\'', '\"'))
    # sys.exit()
    writeValues(json,tmpDir)
    writeFinalFile(resultDir + 'Mapping', json['TriplesMap'].keys())
    #print(json)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", required=False, help="Input excel file")
    parser.add_argument("-l", "--language", required=True, help=("Supported Languages: " + str(supportedLanguages)))
    args = parser.parse_args()
    inputFile = ''

    exist = checkFile(args.input_file)
    if(exist):
            inputFile = str(args.input_file)
    else:
        print("Not input file selected. Using the default xlsx file (data/default.xlsx)")
        inputFile = '../data/default.xlsx'

    if(args.language.lower() not in supportedLanguages):
        print("The selected Language is not supported by the moment.")
        print("Suporteds Languages: " + str(supportedLanguages))
        sys.exit()
    else:
        global templatesDir
        templatesDir += args.language.lower() + "/"
        print(templatesDir)
        generateMapping(inputFile)
        print("Your Mapping File is in ../result/")

if __name__ == '__main__':
    main()
    
