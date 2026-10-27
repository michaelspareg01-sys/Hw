#!/bin/bash
# usage: findpage.sh file.pdf regex  -> page numbers containing regex
f="$1"; pat="$2"; n=$(pdfinfo "$f" 2>/dev/null | awk '/^Pages/{print $2}')
for ((p=1;p<=n;p++)); do pdftotext -f $p -l $p -layout "$f" - 2>/dev/null | grep -qE "$pat" && echo -n "$p "; done; echo
