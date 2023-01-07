[![GitHub license](https://img.shields.io/github/license/djsudduth/keep-it-markdown)](https://github.com/djsudduth/keep-it-markdown/blob/main/LICENSE)

# mindmap-markdown
Mindmap-markdown or mindmd converts Simplemind mind maps to markdown pages as an extension to Simplemind's export function. The script will execute on Windows, MacOS or Linux.

One of the key problems with Simplemind exports is that not all information is exported such as outer notes and relations. Plus, having a markdown outline of the mind map allows for notetaking apps like Obsidian or Logseq to consume the outline easily. Mindmd will export inner and outer notes, notes on node-to-node links, embedded and linked images, urls, and relations between nodes. Audio files (only audio links), node colors and icons are not exported.

## Usage
To run mindmd you need to first add your input and output paths to the `settings.cfg` file. However, you can simply test the script by running:
```bash
> python mindmd.py 
```
This will execute the example test .smmx file found in the `mindmaps` directory to see the markdown output. The default input path is the `mindmaps` folder. The default output path is the `markdown` folder. Output folders will be created dynamically. (Windows users should use forward slashes, e.g. -> c:/md-files/export)

###  Options
All configurations should first be setup in the `settings.cfg` file. If you need to run test files simply change the `test_file_name` to your .smmx file.

#### Switches
To specify a specfic input and output name:
```bash
> python mindmd.py -i inputname.smmx -o outputname.md
```
(paths will be pulled from the settings file)

To run a batch conversion on a simgle directory:
```bash
> python mindmd.py -d 1
```
Mindmd will convert all .smmx files in a flat directory (no subdirectories) with the same name to markdown

To add line numbers to each node in the markdown output:
```bash
> python mindmd.py -n 1
```

#### Titles
Exported note titles use Keep titles in conversion as best it can. In many cases Keep notes do not have titles and by default KIM will use the create date-time as the title. If you wish to use the beginning body content for blank Keep titles use
```bash
> python kim.py -c
```

#### Overwriting or Skipping
KIM by default does not overwrite markdown files when exporting, principally because Keep notes can have the same titles. KIM will try to rename duplicate notes. However, notes can be overwritten with
```bash
> python kim.py -o
```