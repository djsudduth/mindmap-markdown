#!/usr/bin/env python3
import os
import zipfile
import argparse
import shutil
import configparser
import xml.etree.ElementTree as ET
from dataclasses import dataclass, fields

SMMAP_TOPICS = "./mindmap/topics/topic"
SM_GUID = "./mindmap/meta/guid"
DEFAULT_MINDMAP = "document/mindmap.xml"
CONFIG_FILE = "settings.cfg"
DEFAULT_SECTION = "SETTINGS"

default_settings = {
    'input_path': "",
    'output_path': "",
    'media_path': "",
    'test_file_name': ""
}


@dataclass
class Test:
    id: str 
    parent: str
    title: str

@dataclass
class Node:
    id: str =" -1"
    parent: str = "0"
    title: str = ""
    note: str = ""
    outernote: str = ""
    link: str = ""
    relationnote: str = ""
    image: str = ""
    embedded_image: str = ""
    voice_memo: str = ""


node_dict = {
    "id": "-1",
    "object": None,
    "title": "",
    "note": "",
 }

def unzip_file(zippath, filepath):
    extracted_file = zipfile.ZipFile(zippath)
    extracted_file.extractall(filepath)


def load_configs():
    config = configparser.ConfigParser()
    configdict = {}

    cfile = config.read(CONFIG_FILE)
    if not cfile:
        config[DEFAULT_SECTION] = default_settings
        try:
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            raise Exception(e)

    options = config.options(DEFAULT_SECTION)
    for option in options:
        configdict[option] = \
            config.get(DEFAULT_SECTION, option)
    return configdict

    

def parse_mind_map(infile):
 
    plist = {}
    sm_nodes = []
    sorted_nodes = []

    tree = ET.parse(infile)

    print ("Parsing SimpleMind Map...")     
    root = tree.getroot()

    meta = root.findall(SM_GUID)
    for m in meta:
        guid = m.get('guid')

    topics =  root.findall(SMMAP_TOPICS)

    for topic in topics:
        
        topic_node = Node()

        plist[topic.get('id')] = topic.get('parent')
        topic_node.id = topic.get('id')
        topic_node.title = topic.get('text').replace('\\N',' ')
        topic_node.parent = topic.get('parent')
        #topic_node.guid = topic.get('guid')
      
        for note in topic.findall("note"):
            topic_node.note +=  note.text.strip().replace('\n',' ') 
        for child in topic.findall("children/text/note"):
            topic_node.outernote += "Outer Note: " + (child.text and child.text.replace('\n',' ') or "None") 
        for relation in topic.findall("parent-relation/children/text/note"):
            topic_node.relationnote += "Relation Note: (" + topic.get('parent') + ") " +  relation.text.replace('\n', ' ')
        for image in topic.findall("images/image"):
            topic_node.image += image.get('name').replace('\n', ' ') + ".png"
        for link in topic.findall("link"):
            if "diagramref" in link.attrib:
                topic_node.link += link.get('diagramref').replace('\n', ' ')
            else:
                topic_node.link += link.get('urllink').replace('\n', ' ')
        for embedded_image in topic.findall("embedded-image"):
            topic_node.embedded_image += embedded_image.get('name').replace('\n', ' ') + ".png"
        for voice_memo in topic.findall("voice-memo"):
            topic_node.voice_memo += voice_memo.get('link').replace('\n', ' ')
 
   
        sm_nodes.append(topic_node)

    return sm_nodes



def format_map(parent_value, tree_nodes, a, level, numbered):

    configdict = load_configs()
    in_path = configdict["input_path"]
    out_path = configdict["output_path"]
    media_path = configdict["media_path"]

    for node in tree_nodes:
        if parent_value == node.parent:
            my_id = node.id
            relnote = tree_nodes[int(my_id)].relationnote

            #Outer notes only first
            if len(relnote) > 0:
                if relnote.strip().startswith("Relation Note"):
                    a.append("\n" + "\t"*(level) + "--  (*" + relnote + "*)\n")
            if numbered:
                a.append("\t"*(level) + "- (" + str(my_id) + ") " + tree_nodes[int(my_id)].title + "\n") 
            else:
                a.append("\t"*(level) + "-  " + tree_nodes[int(my_id)].title + "\n") 

            for field in fields(tree_nodes[int(my_id)]):
                if field.name != 'title' and field.name != 'id' and field.name != 'parent' and field.name != 'relationnote':
                    attr = getattr(tree_nodes[int(my_id)], field.name) 
                    if attr:
                        if field.name != 'image' and field.name != 'embedded_image':
                            if field.name != 'link' and field.name != 'voice_memo':
                                a.append("\t"*(level+1) + "-- *" + attr.strip() + "*\n")
                            else:
                                a.append("\t"*(level+1) + "-- [" + attr + "](" + attr.strip() + ")\n")                           
                        else:
                            a.append("\t"*(level+1) + "- ![](" + media_path + attr + ")\n")
                            #media
                            shutil.copy2("images/" + attr, out_path + media_path + attr)

            
            format_map (my_id, tree_nodes, a, level + 1, numbered)
    return a    




def format_relations(sm_nodes, infile):
    tree = ET.parse(infile)
    root = tree.getroot()
    output_list = []
    output_list.append("\nRelations:\n")
    relations =  root.findall("./mindmap/relations/relation")
    for relation in relations:
        full_relation = "- (" + relation.get('source') + ") " + sm_nodes[int(relation.get('source'))].title
        for note in relation.findall("children/text/note"):
            full_relation += "-> *" + str(note.text).replace('\n', ' ').strip() + "*"
        full_relation += " -> (" + relation.get('target') + ") " + sm_nodes[int(relation.get('target'))].title
        output_list.append(full_relation + "\n")
    return output_list


def write_output(infile, outfile, numbered):
    # load smmx xml content
    sm_nodes = parse_mind_map(infile)

    #output
    f = open(outfile,"w", encoding='utf8')
    a = []
    outline = format_map("-1", sm_nodes, a, 0, numbered)
    for map in outline:
        f.write(map)
        #media
        #shutil.copy2('/src/dir/file.ext', '/dst/dir/newname.ext')


    relations = format_relations(sm_nodes, infile)
    for map in relations:
        f.write(map)
    f.close()



def main():


       #try:
            #return(self._configdict[key])

    configdict = load_configs()
    in_path = configdict["input_path"]
    out_path = configdict["output_path"]
    media_path = configdict["media_path"]
    test_file = configdict["test_file_name"]

    # get filename from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", "-i", type=str, required=False)
    parser.add_argument("--outfile", "-o", type=str, required=False)
    parser.add_argument("--directory", "-d", type=str, required=False)
    parser.add_argument("--numbered", "-n", type=str, required=False)
 
    args = parser.parse_args()
    in_name = args.infile
    out_name = args.outfile
    batch_dir = args.directory
    numbered = args.numbered
    nums = False

    if numbered != None:
        nums = True

    if batch_dir == None:
        if in_name == None:
            if test_file == '':
                print ("No input file or test file name in settings.cfg provided!\n")
                exit()
            else:
                infile = in_path + test_file
        else:
            infile = in_path + in_name

        if out_name == None:
            ext = os.path.splitext(test_file)
            if out_path == '':
                outfile = in_path + ext[0] + ".md"
            else:
                outfile = out_path + ext[0] + ".md"

        else:
            outfile = out_path + out_name 

        unzip_file(infile, '.')
        write_output(DEFAULT_MINDMAP, outfile, nums)

    else:
        batch_dir = out_path
        for filename in os.listdir(in_path):
            f = os.path.join(in_path, filename).replace("\\","/")
            # checking if it is a file
            if os.path.isfile(f):
                ext = os.path.splitext(filename)
                if ext[1] == ".smmx":
                    try:
                        unzip_file(f, '.')
                    except zipfile.BadZipfile:
                        continue
                    outfile = ext[0] + ".md"
                    print (outfile)
                    write_output(DEFAULT_MINDMAP, batch_dir + ext[0] + ".md", nums)



if __name__ == "__main__":
     main()

