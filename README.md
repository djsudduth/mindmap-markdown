[![GitHub license](https://img.shields.io/github/license/djsudduth/keep-it-markdown)](https://github.com/djsudduth/keep-it-markdown/blob/main/LICENSE)

# mindmap-markdown
Mindmap-markdown or mindmd converts [Simplemind](https://simplemind.eu/) mind maps to markdown pages as an additional type to Simplemind's export function. The script will execute on Windows, MacOS or Linux.

One of the key problems with Simplemind exports is that not all information is exported such as outer notes and relations. Plus, having a markdown outline of the mind map allows for notetaking apps like Obsidian or Logseq to consume the outline easily. Mindmd will export inner and outer notes, notes on node-to-node links, embedded and linked images, urls, and relations between nodes. Audio files (only audio links), node colors, mindmap-to-mindmap links and icons are not exported.

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
(paths will be pulled from the `settings.cfg` file)

#### Batch
To run a batch conversion on a simgle directory:
```bash
> python mindmd.py -d 1
```
Mindmd will convert all .smmx files in a flat directory defined in `settings.cfg` (no subdirectories) using the same file name to markdown

#### Line Numbers
To add line numbers to each node in the markdown output use:
```bash
> python mindmd.py -n 1
```

