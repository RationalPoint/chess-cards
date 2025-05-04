#!/usr/local/bin/python
import argparse
import os
import subprocess

msg = "Script for converting and displaying color choices in the colortest.svg file"
parser = argparse.ArgumentParser(description=msg)
parser.add_argument('light',type=str,help="HTML notation for light square color")
parser.add_argument('dark',type=str,help="HTML notation for dark square color")
args = parser.parse_args()

fp = open('colortest.svg','r')
lines = fp.readlines()
fp.close()

for i,line in enumerate(lines):
  s = line.replace('ffce9e',args.light)
  s = s.replace('d18b47',args.dark)
  lines[i] = s

newfile = 'colortest_{}_{}.svg'.format(args.light,args.dark)
fp = open(newfile,'w')
fp.write(''.join(lines))
fp.close()

cmd = ['open','-a','firefox',newfile]
subprocess.run(cmd)
