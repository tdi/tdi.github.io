#!/bin/bash


title="$1"
max_length="${2:-48}"
slug="$({
    tr '[A-Z]' '[a-z]' | tr -cs '[[:alnum:]]' '-'
  } <<< "$title")"
  slug="${slug##-}"
  slug="${slug%%-}"
  slug="${slug:0:$max_length}"

DATE=`date "+%Y-%m-%d %H:%M"`

cat > content/"$slug".md <<POST
Title: $title
Date: $DATE
Tags:
Category:
Slug: $slug



POST

vim content/"$slug".md
