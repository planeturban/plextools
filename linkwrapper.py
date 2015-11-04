#!/usr/bin/env python

import os, re, sys

exts = ["mkv", "avi", "mp4", "ogm", "ts"]

if len(sys.argv) == 1:
	print "No path!"
	exit(1)
path = sys.argv[1]



docache=1
logunmatched=1

logfile = "/tmp/linkwrapper.log"
log = open(logfile, "a")

map = {}
map['csi'] = ['csi.crime.scene.investigation']
map['csi.new.york'] = ['csi.ny']
map['battlestar.galactica'] = ['battlestar.galactica.2003', 'battlestar.galatica']
map['forever.us'] = ['forever.2014']
map['law.and.order.special.victims.unit'] = ['law.and.order.svu']
map['the.daily.show'] = ['the.daily.show.with', 'the.daily.show.with.jon.stewart']
map['hart.of.dixie'] = ['hart.if.dixie']
map['ncis.los.angeles'] = ['ncis.la']


mirrorpath = "/mnt/newmirror/" + path.split("/")[2] + "/"
links = {} 
realpath=[]
linkfiles=[]

tmp = path.split("/")
tmp[0:3] = []
relative = "/".join(tmp)

def rematch(pattern, inp):
	matcher = re.compile(pattern)
	matches = matcher.match(inp)
	if matches:
		yield matches


def createlink(root, file):
	source = os.path.join(root,file)
	ext = os.path.splitext(file)[1][1:]
	tmp = root.split("/")[-1].lower()
	name = ""
	episode = ""
	matched = 0
	for m in rematch("(.*)[_\.](\d{4})[\._](\d{2})[\._](\d{2}).*", tmp):
		name = re.sub("_", ".", m.group(1))
		season = int(m.group(2))
		episode = "%d.%02d.%02d" % ( int(m.group(2)), int(m.group(3)), int(m.group(4)) )
		matched = 1
	for m in rematch("(.*)[\._]s{0,1}(\d+)[eExX](\d+).*$", tmp):
		if matched:
			continue
		name = re.sub("_", ".", m.group(1))
		season = int(m.group(2))
		episode = "%02dx%02d" % ( int(m.group(2)), int(m.group(3)) )
		matched = 1
	for m in rematch("(.*)[_\.]part[_\.]{0,1}(\d+).*$", tmp):
		if matched:
			continue
		name = re.sub("_", ".", m.group(1))
		season = 1
		episode = "%02dx%02d" % (season, int(m.group(2)) )
		matched = 1
	if not matched: 
		if source not in realpath:
			log.write("Unmatched: %s\n" % source)
		return
	for mapname in map:
		if name in map[mapname]:
			name = mapname
	linkfile = "%s_%s.%s" % ( name, episode, ext)	
	linkpath = "%s%s/s%02d/" % ( mirrorpath, name, season)
	if name in links:
		if episode in links[name]:
			linkfile = ""
	if linkfile:
		if not os.path.exists(linkpath):
			os.makedirs(linkpath)	
		if not os.path.exists(linkpath + linkfile):
			os.symlink(source, linkpath + linkfile)

if not os.path.ismount("/mnt/" + path.split("/")[2]):
	exit(0)	

if docache and os.path.isdir(path):
	for root, dirs, files in os.walk(mirrorpath + relative):
		for file in files:
			linkfile = os.path.join(root, file)
			if os.path.islink(linkfile):
				if not os.path.isfile(linkfile):
					os.remove(linkfile)
				else:
					r = os.readlink(linkfile)
					realpath.append(r)
					for m in rematch("^(.*)_(.*)", file):
						if not m.group(1) in links:
							links[m.group(1)] = []
						links[m.group(1)].append(os.path.splitext(m.group(2))[0])
if os.path.isfile(path):
	tmp = path.split("/")[-1]
	createlink("/".join(path.split("/")[:-1]), tmp)
elif os.path.isdir(path):
	for root, dirs, files in os.walk(path):
		for file in files:
			source = os.path.join(root,file)
			size = os.path.getsize(source)
			ext = os.path.splitext(file)[1][1:]
			if any(ext in e for e in exts) and size > 50146010 and not "sample" in file.lower():
				createlink(root, file)
log.close()
