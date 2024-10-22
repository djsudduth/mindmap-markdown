[![GitHub license](https://img.shields.io/github/license/djsudduth/keep-it-markdown)](https://github.com/djsudduth/keep-it-markdown/blob/main/LICENSE)

# mindmap-markdown
Mindmap-markdown or **mindmd** converts [Simplemind](https://simplemind.eu/) mind maps to either a **single markdown outline** or an **Obsidian Canvas** as additional types to Simplemind's export function. **Simplemind is an amazing mind mapping application** that is free on mobile devices with significant capabilities to capture information. 

One of the key missing components with Simplemind exports is that not all information is exported such as outer notes and relations. Plus, having a markdown outline or canvas of the mind map allows for notetaking apps like Obsidian or Logseq to consume the outline easily. 

Mindmd will export inner and outer notes, notes on node-to-node links, embedded and linked images, urls, and relations between nodes. Audio files (only audio links), node colors, checkboxes, mindmap-to-mindmap links and icons are not exported. The script will execute on Windows, MacOS or Linux.

## Examples

### Markdown Outline

Here is the default example Simplemind mindmap markdown outline screenshot that is located in the **mindmaps** folder:

![](mindmaps/HII%20Regions%20Example.png)

The [example converted markdown](https://github.com/djsudduth/mindmap-markdown/blob/main/markdown/HII%20Regions.md) file is found in the **markdown** folder where the first few lines of the markdown output outline has a format like:

- Nebulae Emissions
	- Types
		- Planetary Nebulae
			- (image here)
		- ~~<u>***HII Regions***</u>~~
			- Orion Nebula
				- The radius of the Orion Nebula is a few parsecs
                - .....


Title and note text formatting in Simplemind is converted as best as possible to markdown formatting. Underline, Superscript and Subscripts are converted to html tags. 

### Obsidian Canvas
The canvas feature allows you to create an Obsidian Canvas from Simplemind nodes that are exported to individual markdown notes that includes their inner and outer text.

An example of the sample canvas file output of the mindmap can be seen here:
![](markdown/HII%20Regions%20Canvas.png)

(Obsidian users please refer to the proper configuration below)

## Usage
To run mindmd in outline mode you can either set your input and output paths in `settings.cfg` file, or, use the input `-i` or output `-o` switches to override the config file.

There are default paths already set in the `settings.cfg` file. However, you can simply test the script against the sample .smmx file by running:
```bash
> python mindmd.py 
```
This will execute the example test .smmx file found in the `mindmaps` directory to see the markdown output. The default input path is the `mindmaps` folder. The default output path is the `markdown` folder. Output folders will be created dynamically. (Windows users should use forward slashes, e.g. -> c:/md-files/export)

###  Options
All configurations should first be setup in the `settings.cfg` file. If you need to run test files simply change the `test_file_name` to your .smmx file.

#### Switches
To specify a specfic input and output path and name:
```bash
> python mindmd.py -i mindmaps/inputname.smmx -o markdown/outputname.md
```
(paths will be pulled from the `settings.cfg` file if the -i or -o switches are not used)  
If you need to use the same directory as mindmd, prefix the files with `./` like `-i ./inputname.smmx`. If an input or output switch isn't provided then the settings path with be used. 

#### Batch
To run a batch conversion on a single directory:
```bash
> python mindmd.py -d
```
Mindmd will convert all .smmx files in a flat directory defined in `settings.cfg` (no subdirectories) using the same file name to markdown. You can also set the input directory with the `-i` switch: 
```bash
> python mindmd.py -d -i mysmmxfolder
```

#### Line Numbers
To add line numbers to each node in the markdown output use:
```bash
> python mindmd.py -n
```

#### Obsidian Canvas
To output the mindmap to an Obsidian canvas vs. a single markdown outline file, use the `-c` switch along with the input flag if needed:
```bash
> python mindmd.py -c
```
or  
```bash
> python mindmd.py -c -i myfiles/coolmindmap.smmx
```
This will create individual markdown files for every mindmap node vs a single output file. Plus, the canvas file will be output. If your mindmap is large you will have many markdown files!  

**Try to use the default file and settings to test this at first**  

Be aware that if you want to export directly to the Obsidian vault, just having an output path isn't enough since a canvas needs to know where the parent vault is located.  Be sure to set the parent vault name in `settings.cfg`  called `obsidian_vault_name`. If your vault is located `c:/Documents/Notes/MyVault` the vault name is just `MyVault`. `Mindmd` can then determine where the canvas, markdown files and media can go.  

You can also set the scale factor to widen or reduce the separation of nodes on the Canvas in `settings.cfg` using `canvas_scale`. Values of about 2.0 to 4.0 seem to work well.  

Note that the media path is relative to the output path in `settings.cfg`

**Canvas mode does not support batch output yet!**

###  Markdown
The markdown outline output will have a tree structure that is well suited for either Obsidian or Logseq notes. Bullets are added to be compatible with Logseq - but future versions will have a flag to remove them if needed.

The canvas file output is only supported by Obsidian. Logseq whiteboards are not yet supported.

An example output file can be found in the `markdown` directory

