#!/usr/bin/python3
# Title           : build_req_table.py
# Description     : Tool to generate a compliance matrix table for standards, autonumbered content
# Author          : Jeffrey Gilbert <jeffrey.t.gilbert@nasa.gov>
# Date            : Oct 18 2021
# Version         : 0.1
# Notes           :
# 

import sys

if __name__=="__main__":
  _doc = []
  _reqkey = ""
  _reqs = {}
  _reqnum = 0

  # System file to open
  if sys.argv[1] == "":
    print("File name is required, use: python3 <path_to>/build_req_table.py <filename>")
    sys.exit(1)

  # fix-for-utf8: on Windows system the console may end up in non-utf8 encoding. make sure to force open statements
  with open(sys.argv[1], "r", encoding="utf8") as f:
    _doc = f.read().splitlines()

  # While most of the content will be single line (at least at first) this script will work
  # with multiple line blocks in either verse, sidebar, quote, or source blocking. 
  #
  # Using blocking and bounding to determine multiple line content in format like:
  # .({reqkey}-R{counter:requirement})
  # [verse]
  # ____
  # text one
  #
  # other line
  # ____
  _inblock = False
  _bound = False
  _current_req = []
  # keep track of structure
  _numbered = False
  _section = "0"
  _description = ""
  # track comment block and ignore
  _in_comment_block = False
  # process the input file
  for _line in _doc:
    if _line.find("////") == 0 and not _in_comment_block:
      _in_comment_block = True
    elif _line.find("////") == 0 and _in_comment_block:
      _in_comment_block = False
      continue
    if _in_comment_block:
      continue
    if _line.find("//") == 0:
      # single line comment
      continue
    # check for reqkey
    if _line.find(":reqkey:") != -1:
      _reqkey = _line.split(" ",1)[1]
    # check for current location
    #  make sure we are considering asciidoc numbered and not numbered, stop at appendix
    if _line.find(":numbered:") != -1:
      _numbered = True
    elif _line.find(":!numbered:") != -1:
      _numbered = False
    elif _line.find("[appendix]") != -1:
      _numbered = False
    # Now consider if the line is a section or subsection line and figure out the numbering and 
    # gather info for later use
    if _line.find("=") == 0 and _line.rfind("=") > 0 and _numbered and _line.find(" ") != -1:
      # new section, update desicription
      _description = _line.split(" ", 1)[1]
      #print(_line)
      # figure out the next subsection (same size, lower, higher), if '== ' then new section
      if _line.find(" ") == 2:
        _section = "{}".format(int(_section.split(".")[0]) + 1)
      elif _line.find(" ")-1 == len(_section.split(".")):
        _section = "{}.{}".format(_section[0:_section.rfind(".")], int(_section[_section.rfind(".")+1:])+1)
      elif _line.find(" ")-1 > len(_section.split(".")):
        _section = "{}.1".format(_section)
      elif _line.find(" ")-1 < len(_section.split(".")):
        #print("  {}".format(_section))
        #print("  {}".format(_section.split(".")[0:_line.find(" ")-2]))
        #print("  {}".format(_section.split(".")[_line.find(" ")-2]))
        _stub = _section.split(".")[0:_line.find(" ")-2]
        _inc = int(_section.split(".")[_line.find(" ")-2]) + 1
        _section = "{}.{}".format(".".join(_stub), _inc)
      #print("+ {}".format(_section))
      continue
    # key on counter:requirement
    if _line.find("counter:requirement") != -1:
      # increment reqnum
      _reqnum = _reqnum + 1
      # dot on first line indicates title value in block text unless it has a space after, which could be a bullet
      if _line[0] == "." and _line[1] != " ":
        _inblock = True
        continue
      else:
        #print("{}, {}".format(_reqkey, _reqnum))
        # otherwise assume it is a single line requirement
        # check for it being a bullet
        if _line[1] == " ":
          _reqs["{}-R{}".format(_reqkey, _reqnum)] = { "raw_text": _line.split(" ", 2)[2], "section": _section, "description": _description }
        else:
          _reqs["{}-R{}".format(_reqkey, _reqnum)] = { "raw_text": _line.split(" ", 1)[1], "section": _section, "description": _description }
        continue
    # if we are outside of the req title check for being in the block format
    if _inblock and not _bound:
      #print(_line[0:4])
      # allow for different block delimiters and if found we next go inside the boundary
      if _line[0:4] == "____" or _line[0:4] == "****" or _line[0:4] == "----" or _line[0:4] == "....":
        _bound = True
        continue
    # with in block and in bound we want to start to remember the text
    if _inblock and _bound:  
      # when we find the next delimiter of the block exit out of block and bound set value and reset holding
      if _line[0:4] == "____" or _line[0:4] == "****" or _line[0:4] == "----" or _line[0:4] == "....":
        _inblock = False
        _bound = False
        # add the current req to the data block, remove newlines and add the req number into it
        _key = "{}-R{}".format(_reqkey, _reqnum)
        _reqs[_key] = { "raw_text": " ".join(_current_req), "section": _section, "description": _description }
        _current_req = []
      else:
        _current_req.append(_line)

  #print(_reqs)
  _counter = 0
  # process the requirement text into table
  _output = []
  _output.append('[width="100%",cols="1,3,3,1,2"]')
  _output.append('|====')
  _output.append('|Section |Description |Requirement |Applicable | Comments')
  _output.append('')
  for _k,_v in _reqs.items():
    _output.append("|{}".format(_v["section"]))
    _output.append("|{}".format(_v["description"]))
    _output.append("|*({})* {}".format(_k, _v["raw_text"]))
    _output.append("|")
    _output.append("|")
    _output.append('')
  _output.append('|====')

  # fix-for-utf8: on Windows system the console may end up in non-utf8 encoding. make sure to force open statements
  with open('std-compliance-matrix.adoc', 'w', encoding="utf8") as f:
    f.write("\n".join(_output))


