#!/usr/bin/env python3
"""Extract body tables from downloaded official documentation."""
from html.parser import HTMLParser
from pathlib import Path
import sys
class Tables(HTMLParser):
    def __init__(self): super().__init__(); self.depth=0; self.rows=[]; self.row=[]; self.cell=None; self.tables=[]
    def handle_starttag(self,tag,attrs):
        if tag=='table': self.depth+=1
        if self.depth and tag=='tr': self.row=[]
        if self.depth and tag in ('td','th'): self.cell=[]
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None: self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
        if tag=='tr' and self.depth: self.rows.append(self.row)
        if tag=='table':
            self.depth-=1
            if not self.depth: self.tables.append(self.rows); self.rows=[]
E=Path(__file__).resolve().parent/'evidence'
for key in sys.argv[1:]:
    p=Tables(); p.feed((E/(key+'.html')).read_text()); print('\nSOURCE',key)
    for i,table in enumerate(p.tables):
        print('TABLE',i)
        for row in table[:70]: print(' | '.join(row))
