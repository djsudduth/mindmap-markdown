#!/usr/bin/env python3
import os
import re
import math
import zipfile
import hashlib
import argparse
import shutil
import json
import uuid
import random
import time
import string
import configparser
import xml.etree.ElementTree as ET
from dataclasses import dataclass, fields
from pathlib import Path

SMMAP_TOPICS = "./mindmap/topics/topic"
SM_GUID = "./mindmap/meta/guid"
DEFAULT_MINDMAP = "document/mindmap.xml"
CONFIG_FILE = "settings.cfg"
DEFAULT_SECTION = "SETTINGS"

default_settings = {
    'input_path': "",
    'output_path': "",
    'media_path': "",
    'test_file_name': "",
    'canvas_scale': "",
    'obsidian_vault_name': ""
}


@dataclass
class Test:
    id: str 
    parent: str
    title: str

@dataclass
class Relation:
    from_node: int = 0
    to_node: int = 0
    text: str = ""

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
    image_pos: str = ""
    cimages: str = ""
    embedded_image: str = ""
    voice_memo: str = ""
    x: str = ""
    y: str = ""
    guid: str = ""


@dataclass
class FilePaths:
    in_path_exists: bool = False
    in_file_exists: bool = False
    in_seems_filelike: bool = False
    in_path: str = ""
    in_file: str = ""
    in_full_path: str = ""
    out_path_exists: bool = False
    out_file_exists: bool = False
    out_seems_filelike: bool = False
    out_path: str = ""
    out_file: str = ""
    out_full_path: str = ""
    out_full_media_path: str = ""



node_dict = {
    "id": "-1",
    "object": None,
    "title": "",
    "note": "",
 }

media_files = []

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


def normalize_path(path):
    #Normalizes a relative path by resolving "../" components.

    parts = path.split('/')
    normalized_parts = []
    for part in parts:
        if part == '..':
            if normalized_parts:
                normalized_parts.pop()
        else:
            normalized_parts.append(part)
    return '/'.join(normalized_parts)


class CanvasNode:
  """Represents a node in Canvas"""
  def __init__(self, type=None, file=None, title=None, text=None, id=None, x=0, y=0, width=0, height=0, color=2):
    self.type = type
    self.file = file
    self.title = title
    self.text = text
    self.id = id
    configs = load_configs()
    self.canvas_scale = float(configs["canvas_scale"])
    self.x = int((x - 500) * self.canvas_scale)
    self.y = int((y - 500) * self.canvas_scale)
    self.width = width
    self.height = height
    #self.color = color


class CanvasEdge:
  """Represents an edge in Canvas"""
  def __init__(self, id=None, fromNode=None, fromSide=None, toNode=None, toSide=None, label=None):
    self.id = id
    self.fromNode = fromNode
    self.fromSide = fromSide
    self.toNode = toNode
    self.toSide = toSide
    self.label = label

class Canvas:
  def __init__(self, title):
    self.nodes = []
    self.edges = []
    self.title = title
    self.base_path = ""  
    self.canvas_path = ""
    

  def set_base_path(self, base_path, canvas_vault):
    self.base_path = base_path
    tpath = base_path.split(os.path.join(canvas_vault, '').replace("\\","/"))
    if len(tpath) > 0:
        self.canvas_path = tpath[len(tpath) - 1]
    else:
        self.canvas_path = ""

  def add_node(self, node, type, text):
    if not isinstance(node, CanvasNode):
      raise TypeError("Invalid node type. Must be a Node object.")
    self.nodes.append(node)
    # Create file for "file" type nodes
    if type == ".md" or type ==".png": # and node.file:
        extension = type 
        pattern = r"[\\/:*?\"<>|]"
        note_file = re.sub(pattern, '', node.title)
        file_path = f"{self.base_path}{note_file}{extension}"
        node.file = f"{self.canvas_path}{note_file}{extension}"
        node.file = normalize_path(node.file)
        if type == ".md":
            # Create the file
            with open(file_path, "wb") as f:
                f.write(text.encode())  # Placeholder content
            print(f"Created file: {file_path}")
            
   # elif type == "img":


  def add_edge(self, edge):
    if not isinstance(edge, CanvasEdge):
      raise TypeError("Invalid edge type. Must be an Edge object.")
    self.edges.append(edge)

  def object_to_json(self):
    if not hasattr(self, "nodes") or not hasattr(self, "edges"):
      raise ValueError("Object must have 'nodes' and 'edges' attributes.")

    # Convert nodes and edges to dictionaries
    node_dicts = [node.__dict__ for node in self.nodes]
    edge_dicts = [edge.__dict__ for edge in self.edges]

    # Create the JSON structure
    json_data = {"nodes": node_dicts, "edges": edge_dicts}
    return json.dumps(json_data, indent=4)
  

def determine_relative_position(node1: CanvasNode, node2: CanvasNode) -> str:
    # Calculate the bounding box of each rectangle
    rect1_left = float(node1.x)
    rect1_top = float(node1.y)
    rect1_right = rect1_left + float(node1.width)
    rect1_bottom = rect1_top - float(node1.height)

    rect2_left = float(node2.x)
    rect2_top = float(node2.y)
    rect2_right = rect2_left + float(node2.width)
    rect2_bottom =  rect2_top - float(node2.height)

      # Check if rectangles overlap
    #if rect1_left < rect2_right and rect2_left < rect1_right and rect1_top > rect2_bottom and rect2_top > rect1_bottom:
    #    return "overlapping"

    # Calculate the angle between the centers of the rectangles
    center1_x = (rect1_left + rect1_right) / 2
    center1_y = (rect1_top + rect1_bottom) / 2
    center2_x = (rect2_left + rect2_right) / 2
    center2_y = (rect2_top + rect2_bottom) / 2
    # Inverted axis ??
    angle = math.degrees(math.atan2(-(center2_y - center1_y), center2_x - center1_x)) - 90

    # Adjust the angle to be in the range 0 to 360
    if angle < 0:
        angle += 360

    # Determine the relative position based on the angle
    if 0 <= angle <= 45:
        return "top,bottom"
    elif 45 < angle <= 135:
        return "left,right"
    elif 135 < angle <= 225:
        return "bottom,top"
    elif 315 < angle <= 359:
        return "top,bottom"
    else:
        return "right,left"

    
  

canvas = Canvas("Null")


def unzip_file(zippath, filepath):
    extracted_file = zipfile.ZipFile(zippath)
    extracted_file.extractall(filepath)

def validate_files(in_filepath, out_filepath, media_path):
    fs = FilePaths()
    i = check_file_path(in_filepath)
    fs.in_path_exists = i[0]
    fs.in_file_exists = i[1]  
    fs.in_seems_filelike = i[2]
    fs.in_full_path = os.path.join(in_filepath, '').replace("\\","/")
    if fs.in_seems_filelike:
        fs.in_full_path = fs.in_full_path.rstrip('/')
    fs.in_path = i[3]
    fs.in_file = i[4]
    i = check_file_path(out_filepath)
    fs.out_path_exists = i[0]
    fs.out_file_exists = i[1]  
    fs.out_seems_filelike = i[2]
    fs.out_full_path = os.path.join(out_filepath, '').replace("\\","/")
    if fs.out_seems_filelike:
        fs.out_full_path = fs.out_full_path.rstrip('/')
    fs.out_path = i[3]
    fs.out_file = i[4]
    fs.out_full_media_path = fs.out_path + media_path
    return (fs)



def check_file_path(filepath):
    foundfile = False
    foundpath = False
    seemslikefile = False

    if filepath is not None:
        if "." not in filepath:
            filepath = os.path.join(filepath, '').replace("\\","/")
        else:
            seemslikefile = True
        pathname, filename = os.path.split(filepath)    
        pathname = os.path.join(pathname, '').replace("\\","/")
        if os.path.exists(pathname):
            foundpath = True
            a = os.path.isfile(filepath)
            if seemslikefile and os.path.isfile(filepath):
                foundfile = True

    return(foundpath, foundfile, seemslikefile, pathname, filename)



# Replace simplemind rtf formatting syntax with markdown and html
def replace_html_endtag(text):
  html = ["<u>", "<sup>", "<sub>"]
  for html_pre in html:
    html_post = re.sub("<", "</", html_pre)
    count = 1
    def replace_func(match):
      nonlocal count
      count += 1
      return html_post if count % 2 != 0 else html_pre
    text=re.sub(html_pre, replace_func, text)
  return(text)

def replace_with_markdown(text):
    if text is not None:
        std_md = re.sub(r"\\\\", r"\\", text)
        std_md =  re.sub(r"\\~", "~~", re.sub(r"\\\*", "**", re.sub(r"\\/", "*", std_md)))
        return (replace_html_endtag(
            re.sub(r"\\_", "<u>", re.sub(r"\\\^", "<sup>", re.sub(r"\\`", "<sub>", std_md)))))
    else:
        return()



def parse_mind_map(infile):
 
    plist = {}
    sm_nodes = []
    sorted_nodes = []

    xml_file = open(infile, 'r', encoding='utf-8')
    tree = ET.parse(xml_file)

    #print ("Parsing SimpleMind Map...")     
    root = tree.getroot()

    meta = root.findall(SM_GUID)
    for m in meta:
        guid = m.get('guid')

    topics =  root.findall(SMMAP_TOPICS)

    for topic in topics:
        
        topic_node = Node()

        plist[topic.get('id')] = topic.get('parent')
        topic_node.id = topic.get('id')
        #topic_node.title = topic.get('text').replace('\\N',' ')
        topic_node.title = replace_with_markdown(topic.get('text'))
        if topic_node.title is not None and type(topic_node.title) != tuple:
            topic_node.title = topic_node.title.replace('\\N',' ')
        else:
            topic_node.title = topic.get('guid')

        topic_node.x = topic.get('x')
        topic_node.y = topic.get('y')
        g = topic.get('guid')
        if not g:
            g = uuid.uuid4().hex
        topic_node.guid = string_to_hexhash(g, 16)
        topic_node.parent = topic.get('parent')
        #topic_node.guid = topic.get('guid')
      
        for note in topic.findall("note"):
            topic_node.note += replace_with_markdown(note.text.strip().replace('\n',' '))
        for child in topic.findall("children/text/note"):
            topic_node.outernote += "*Outer Note*: " + replace_with_markdown((child.text and child.text.replace('\n',' ') or "None")) 
        for relation in topic.findall("parent-relation/children/text/note"):
            topic_node.relationnote += "*Relation Text*: (" + sm_nodes[int(topic.get('parent'))].title + ") " +  replace_with_markdown(relation.text.replace('\n', ' '))
        for image in topic.findall("images/image"):
            topic_node.image += image.get('name').replace('\n', ' ') + ".png"
            topic_node.image_pos += image.get('x') + "," + image.get('y') + ";"
        for cimage in topic.findall("children/image"):
            topic_node.cimages += cimage.get('name').replace('\n', ' ') + ".png"
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



def format_map(parent_value, tree_nodes, a, ee, level, numbered, infile, outfile, vf):

    configdict = load_configs()
    in_path = os.path.join(os.path.split(infile)[0], '').replace("\\","/") #configdict["input_path"]
    out_path = os.path.join(os.path.split(outfile)[0], '').replace("\\","/") #configdict["output_path"]
    media_path = configdict["media_path"]

    for node in tree_nodes:
        if parent_value == node.parent:
            my_id = node.id
            relnote = tree_nodes[int(my_id)].relationnote

            #Outer notes only first
            if len(relnote) > 0:
                if relnote.strip().startswith("*Relation Text*"):
                    a.append("\n" + "\t"*(level) + "--> (" + relnote + ") -->\n")
                    #a.append("\n" + "\t"*(level) + "--> (*" + relnote + "*) -->\n")

            if numbered:
                a.append("\t"*(level) + "- (" + str(my_id) + ") " + tree_nodes[int(my_id)].title + "\n") 
            else:
                a.append("\t"*(level) + "- " + tree_nodes[int(my_id)].title + "\n") 
            ee.append(str(node.parent) + "," + str(node.guid) + "," + str(level))

            for field in fields(tree_nodes[int(my_id)]):
                if field.name != 'title' and field.name != 'id' and \
                    field.name != 'parent' and field.name != 'relationnote' and \
                    field.name != 'x' and field.name != 'y' and field.name != 'guid' and \
                    field.name != 'image_pos' and field.name != 'cimages':
                    attr = getattr(tree_nodes[int(my_id)], field.name) 
                    if attr:

                        if field.name != 'image' and field.name != 'embedded_image':
                            if field.name != 'link' and field.name != 'voice_memo':
                                a.append("\t"*(level+1) + "- " + attr.strip() + "\n")
                                #a.append("\t"*(level+1) + "- *" + attr.strip() + "*\n")
                            else:
                                a.append("\t"*(level+1) + "- [" + attr + "](" + attr.strip() + ")\n")                           
                        else:
                            n = 44
                            mfiles = [(attr[i:i+n]) for i in range(0, len(attr), n)]
                            for mfile in mfiles:
                                a.append("\t"*(level+1) + "- ![](" + media_path + mfile + ")\n")
                                #e.append(str(node.parent) + "," + str(media_path + mfile) + "," + "i")
                                #media
                                for attempt in range(1, 2):
                                    try:
                                        shutil.copy2("images/" + mfile, out_path + media_path + mfile)
                                    except Exception as e:
                                        if attempt == 2:
                                            print ("Image file 'images/" + mfile + "' missing or not accessible!!")
                                            continue
                                        time.sleep(0.25)


            
            format_map (my_id, tree_nodes, a, ee, level + 1, numbered, in_path, out_path, vf)
    return a    




def format_relations(sm_nodes, infile, crelations):
    tree = ET.parse(infile)
    root = tree.getroot()
    output_list = []
    output_list.append("\n\n- Relations:\n")
    relations =  root.findall("./mindmap/relations/relation")
    for relation in relations:
        full_relation = "- (" + relation.get('source') + ") " + sm_nodes[int(relation.get('source'))].title
        for note in relation.findall("children/text/note"):
            full_relation += "-> " + replace_with_markdown(str(note.text).replace('\n', ' ').strip())
            #full_relation += "-> *" + str(note.text).replace('\n', ' ').strip() + "*"
        full_relation += " -> (" + relation.get('target') + ") " + sm_nodes[int(relation.get('target'))].title
        output_list.append("\t" + full_relation + "\n")
        canvas_relation = Relation(from_node=int(relation.get('source')), to_node=int(relation.get('target')), text=replace_with_markdown(str(note.text).replace('\n', ' ').strip()))
        crelations.append(canvas_relation)
    return output_list


def write_output(infile, outfile, numbered, vf, ocanvas):
    # load smmx xml content
    sm_nodes = parse_mind_map(infile)

    #output
    f = open(outfile,"w", encoding='utf8')
    a = []
    ee = []
    outline = format_map("-1", sm_nodes, a, ee, 0, numbered, infile, outfile, vf)
    for map in outline:
        if not ocanvas:
            f.write(map)
        #media
        #shutil.copy2('/src/dir/file.ext', '/dst/dir/newname.ext')

    canvas_relations = []
    relations = format_relations(sm_nodes, infile, canvas_relations)
    for map in relations:
        if not ocanvas:
            f.write(map)
    f.close()

    if ocanvas:
        # Future work
        configdict = load_configs()
        out_path = os.path.join(os.path.split(outfile)[0], '').replace("\\","/") #configdict["output_path"]
        media_path = configdict["media_path"]
        canvas_vault = configdict["obsidian_vault_name"]


        for node in sm_nodes:
            canvas.set_base_path(out_path, canvas_vault)
            c_node = CanvasNode(type="file", file = None, title=node.title, text="", id=node.guid, x=float(node.x), y=float(node.y), width=300.00, height=140.00)
            note_text = node.note + "\n\n" + node.outernote
            if len(node.embedded_image) > 0:
                note_text = "![](" + media_path + node.embedded_image + ")\n" + node.link + "\n" + note_text
            canvas.add_node(c_node, ".md", note_text)

        for parent, edge in enumerate(ee):
            pvals = edge.split(",")
            for j, children in enumerate(ee):
                vals = children.split(",")
                if int(vals[0]) == parent:
                    p = determine_relative_position(canvas.nodes[parent], canvas.nodes[j])
                    from_to = p.split(",")
                    relation = sm_nodes[j].relationnote
                    if ":" in relation:
                        relation = relation.split(":")[1].strip().split(")")[1].strip()
                    c_edge = CanvasEdge(string_to_hexhash(uuid.uuid4().hex, 16), pvals[1], from_to[0], vals[1], from_to[1], relation)
                    canvas.add_edge(c_edge)

        imagelist = []
        coordinates = []
        for node in sm_nodes:
            canvas.set_base_path(out_path + media_path, canvas_vault)
            if len(node.image) > 0:
                image_names = re.findall(r"(.{44})", node.image)
                for im in image_names:
                    imagelist.append(im)
                # Extract coordinate pairs
                coordinate_pairs = node.image_pos.split(";")
                for pair in coordinate_pairs:
                    if len(pair) > 0:
                        pair = str(pair)
                        top, left = pair.split(",")
                        coordinates.append((node.id, top, left))
        ex_images = list(zip(imagelist, coordinates))
        for images in ex_images:
            c_node = CanvasNode(type="file", file = None, title=images[0].split(".")[0], text="", 
                    id=string_to_hexhash(uuid.uuid4().hex, 16), x=float(sm_nodes[int(images[1][0])].x) + float(images[1][1]), y=float(sm_nodes[int(images[1][0])].y) + float(images[1][2]), width=300.00, height=140.00)
            canvas.add_node(c_node, ".png", "")

        for crel in canvas_relations:
            p = determine_relative_position(canvas.nodes[crel.from_node], canvas.nodes[crel.to_node])
            from_to = p.split(",")
            c_edge = CanvasEdge(string_to_hexhash(uuid.uuid4().hex, 16), canvas.nodes[crel.from_node].id, from_to[0], canvas.nodes[crel.to_node].id, from_to[1], crel.text)
            canvas.add_edge(c_edge)





def string_to_hexhash(alphanumeric_string, hash_len):
    hash_object = hashlib.sha3_384(alphanumeric_string.encode('utf-8'))
    hexdigest = hash_object.hexdigest()
    start_index = random.randrange(0, len(hexdigest) - hash_len)
    return hexdigest[start_index:start_index + hash_len]



def main():

    print ("\n** Mindmap Markdown v-0.1.0 **\n")
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
    parser.add_argument("--directory", "-d", default=False, action="store_true",
                    help="Flag for batch processing")
    parser.add_argument("--numbered", "-n", default=False, action="store_true",
                    help="Flag for numbered nodes")
    parser.add_argument("--canvas", "-c", default=False, action="store_true",
                    help="Flag for output of Obsidian canvas")
    args = parser.parse_args()


    in_name = args.infile
    out_name = args.outfile
    batch_dir = args.directory
    numbered = args.numbered
    ocanvas = args.canvas
    #ocanvas = True
    nums = False

    if ocanvas and batch_dir:
        print ("Obsidian Canvas output is not yet supported in batch mode!\n")
        exit()

    if numbered:
        nums = True

    if in_name != None:
        in_path = in_name

    if out_name != None:
        out_path = out_name


    vs = validate_files(in_path, out_path, media_path)
    if vs.in_path == '':
        in_path = configdict["input_path"] + in_path
    if vs.out_path == '':
        out_path = configdict["output_path"] + out_path
    vs = validate_files(in_path, out_path, media_path)


    if batch_dir == False:
        if in_name == None:
            if test_file == '':
                print ("No input file or test file name in settings.cfg provided!\n")
                exit()
            else:
                infile = in_path + test_file
                vs.in_file = test_file
        else:
            if vs.in_path_exists == False or vs.in_file_exists == False:
                print ("Input file path and/or name are invalid or missing!\n")
                exit()
            infile = vs.in_full_path

        if out_name == None:
            if vs.out_path_exists == True:
                ext = os.path.splitext(vs.in_file)
                outfile = vs.out_path + ext[0] + ".md"
            else:
                print ("Output file path: " + vs.out_path + " is invalid or missing!\n")  
                exit()
        else:
            if vs.out_path_exists == False or vs.out_seems_filelike == False:
                print ("Output file path: " + vs.out_path + " and/or name are invalid\n")
                exit()
            outfile = vs.out_full_path
        print ("Mindmap: " + infile + " ----> Markdown: " + outfile)
        unzip_file(infile, '.')
        write_output(DEFAULT_MINDMAP, outfile, nums, vs, ocanvas)
        if ocanvas:
            #print (canvas.object_to_json())
            cname = outfile.split(".")[0]
            f = open(cname + ".canvas","w", encoding='utf8')
            f.write(canvas.object_to_json())
            print ("\nCreated file: " + cname + ".canvas")

    else:
        if in_name != None:
            if vs.in_path_exists == False or vs.in_seems_filelike == True:
                print ("Invalid path for batch output: " + vs.in_full_path + " - be sure your input path exists and doesn't contain a file name!")
                exit()
            else:
                in_path = vs.in_full_path #in_name
 

        if out_name != None:
            if vs.out_path_exists == False or vs.out_seems_filelike == True:
                print ("Invalid path for batch output: " + vs.out_full_path + " - be sure your destination path exists and doesn't contain a file name!")
                exit()
            else:
                batch_dir = vs.out_full_path #os.path.join(out_name, '').replace("\\","/")
        else:
            batch_dir = out_path
        for filename in os.listdir(in_path):
            f = os.path.join(in_path, filename) #.replace("\\","/")
            # checking if it is a file
            if os.path.isfile(f):
                ext = os.path.splitext(filename)
                if ext[1] == ".smmx":
                    try:
                        unzip_file(f, '.')
                    except zipfile.BadZipfile:
                        continue
                    outfile = ext[0] + ".md"
                    print ("Mindmap: " + f + " ----> Markdown: " + batch_dir + outfile)
                    write_output(DEFAULT_MINDMAP, batch_dir + ext[0] + ".md", nums, vs, ocanvas)

    if not os.path.exists(vs.out_full_media_path):
        os.makedirs(vs.out_full_media_path)
    for media in media_files:
        try:
            shutil.copy2("images/" + media, vs.out_full_media_path + media)
        except:
            print ("Image file 'images/" + media + "' missing or not accessible!!")
            continue



if __name__ == "__main__":
     main()
