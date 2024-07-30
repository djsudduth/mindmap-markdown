[![GitHub license](https://img.shields.io/github/license/djsudduth/keep-it-markdown)](https://github.com/djsudduth/keep-it-markdown/blob/main/LICENSE)

# mindmap-markdown
Mindmap-markdown or mindmd converts [Simplemind](https://simplemind.eu/) mind maps to markdown pages as an additional type to Simplemind's export function. Simplemind is an amazing mind mapping application that is free on mobile devices with significant capabilities to capture information. 

One of the key missing components with Simplemind exports is that not all information is exported such as outer notes and relations. Plus, having a markdown outline of the mind map allows for notetaking apps like Obsidian or Logseq to consume the outline easily. Mindmd will export inner and outer notes, notes on node-to-node links, embedded and linked images, urls, and relations between nodes. Audio files (only audio links), node colors, checkboxes, mindmap-to-mindmap links and icons are not exported. The script will execute on Windows, MacOS or Linux.

## Example
Here is the default example Simplemind mindmap screenshot that is located in the **mindmaps** folder:

![](mindmaps/HII%20Regions%20Example.png)

The example converted markdown file is found in the **markdown** folder where the first few lines have a format like:

- Nebulae Emissions
	- Types
		- Planetary Nebulae
			- ![](media/5d4493207aed3f31bcc366a6a7bee2c5254c0d02.png)
		- ~~<u>***HII Regions***</u>~~
			- Orion Nebula
				- The radius of the Orion Nebula is a few parsecs


Title and note text formatting in Simplemind is converted as best as possible to markdown formatting. Underline, Superscript and Subscripts are converted to html tags. 

## Usage
To run mindmd you can either set your input and output paths in `settings.cfg` file, or, use the input `-i` or output `-o` switches to override the config file.

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

Note that the media path is relative to the output path in `settings.cfg`

###  Markdown
The markdown output will have a tree structure that is well suited for either Obsidian or Logseq notes. Bullets are added to be compatible with Logseq - but future versions will have a flag to remove them if needed.

An example output file can be found in the `markdown` directory

