#!/bin/bash
# Title         : clean_document_setup.sh
# Description   : A script to assist in making a new document repository for 
#                 ETADS asciidoc-git-workflow
# Author        : Jeffrey Gilbert <jeffrey.t.gilbert@nasa.gov>
# Date          : 2018-07-18
# Version       : 0.1
# Notes         : This will work in Linux, it should work in bash for Mac, we 
#                 may need to have a CLEAN_DOCUMENT_SETUP.BAT version for the 
#                 Windows folks.

# Check that an argument for a document name is present
if [ "$#" -lt 1 ]
then 
  echo -e "\e[91mYou need to supply a document name.\e[0m"
  echo -e "\e[32mShould look like this:\e[0m"
  echo -e "\e[32m.. document_basecamp/script/clean_document_setup.sh \"Name of First Doc\"\e[0m"
fi

# Check to make sure we are not in document_basecamp but in a different git repo
if [[ $( echo $(pwd) | grep -e "document_basecamp" ) ]]
then 
  echo -e "\e[91mThis script needs to be run in a different repository.\e[0m"
  echo -e "\e[32mYou may just need to execute this from one level below\e[0m"
  echo -e "\e[32mthe document_basecamp directory.\e[0m"
  exit 1
fi

# Check to make sure we are not on the master branch
if [[ $( echo $( git rev-parse --abbrev-ref HEAD ) | grep master ) ]]
then 
  echo -e "\e[91mYou can not be on the master branch.\e[0m"
  echo -e "\e[32mTry:\e[0m"
  echo -e "\e[32m.. git branch <newname>\e[0m"
  echo -e "\e[32m.. git checkout <newname>\e[0m"
  echo -e "\e[32mThen rerun this script.\e[0m"
  exit 1
fi

# It should be clean, but not required. Just check that anything conflicting is 
# not in play.

if [ -f "README.md" ]
then
  git mv README.md README.adoc
  sed -i "s/#/=/g" README.adoc
fi

if [ ! -d build ]
then 
  mkdir build
fi

if [ ! -f build/.gitignore ]
then 
  echo "./*" > build/.gitignore
fi

# make the first document

cat > $( echo $1 | sed -e "s/\s/-/g" ).adoc << FIRSTDOC 
= $1
:doctype: article
:pdf-fontsdir: document_basecamp/fonts/
:pdf-stylesdir: document_basecamp/
:stylesdir: document_basecamp/
:pdf-style: asciidoctor-pdf.yml
:stylesheet: asciidoctor.css
:toc: macro
:toc-title: TABLE OF CONTENTS
:toclevels: 3
:toc-placement!:

'''
<<<

// PLACEHOLDER FOR OFFICIAL NOTICE

'''
<<<

DOCUMENT HISTORY LOG

[width="100%",cols="1,1,1,2,4"]
|====
|Status|Document Revision|Change Number|Approval Date|Description

|Draft||||Initial Release

|====

'''
<<<

FORWARD

'''
<<<

toc::[]

'''
<<<

:numbered:

{doctitle}

'''
<<<

FIRSTDOC

# set first document as link in README

echo "("$( echo $1 | sed -e "s/\s/-/g")".adoc)[$1]" >> README.adoc


