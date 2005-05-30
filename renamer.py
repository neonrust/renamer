#! /usr/bin/env python

import re, glob, sys, os, os.path

out=sys.stdout.write
err=sys.stderr.write
prg=os.path.basename(sys.argv[0])



def main(args):
	if len(args)<3:
		err('%s: v0.3.5 - A concoction by Andre Jonsson (2005-02-02)\n' % prg)
		err('Usage [-q] <find-regex> <replace> <files & dirs...>\n')
		err('   -q     By wewwy, wewwy quiet  (and rename without question)\n')
		return 0

	quiet=False
	if args[0]=='-q':
		quiet=True
		args=args[1:]

	try:
		pattern=re.compile(args[0])
	except Exception, msg:
		err('%s: could not compile regular expression: %s\n%s' % (prg, args[0], msg))
		return 1

	replace=args[1]
	files=args[2:]

	fileList={}
	for f in files:
		fileList[f]=1

	if not fileList:
		err('%s: No files matched.\n' % prg)
		return 1

	fileList=fileList.keys()
	fileList.sort()

	renamings=[]
	for name in fileList:
		newName=strReplace(pattern, replace, name)
		renamings.append((name, newName))

	# remove renames that didn't result in a change
	newRenamings=[]
	for name, newName in renamings:
		if newName != name:
			newRenamings.append((name, newName))
	renamings=newRenamings

	if not renamings:
		err('%s: nothing to rename after no-ops removed.\n' % prg)
		return 0

	if not validateRenamings(renamings):
		return 1

	if not quiet:
		for name, newName in renamings:
			out('  rename:  "%s" -> "%s"\n' % (name, newName))

	if not quiet:
		try:
			answer=raw_input('** Continue with rename? [Y/n] ').strip()
			if answer=='n':
				return 0
		except:
			out('aborted\n')
			return 255

	for rename in renamings:
		name, newName = rename
		try:
			createDirectories(os.path.dirname(newName))
			os.rename(name, newName)
		except Exception, msg:
			err('%s: renaming "%s" to "%s" failed: %s\n' % (prg, name, newName, msg))

	return 0


def strReplace(pattern, replace, name):
	idx=0
	while 1:
		m=pattern.search(name[idx:])
		if not m:
			return name
		
		name=name[0:idx+m.start()] + m.expand(replace) + name[idx+m.end():]
		idx=m.start()+len(replace)

	return name


def validateRenamings(renamings):
	# check empty names
	for name, newName in renamings:
		if not newName:
			err('%s: can not rename to empty name: "%s" -> "%s"\n' %
				(prg, name, newName))
			return False
		if newName in ('.', '..', '/'):
			err('%s: can not rename: "%s" -> "%s"\n' % (prg, name, newName))
			return False


	# check if renamed files collide
	for idx0 in range(len(renamings)):
		for idx1 in range(len(renamings)):
			if idx0==idx1:
				continue
			if renamings[idx0][1]==renamings[idx1][1]:
				err('%s: rename collision: "%s" & "%s" -> "%s"\n' %
					(prg, renamings[idx0][0], renamings[idx1][0], renamings[idx0][1]))
				return False

	# check if any renamed file collide with any, not yet renamed, original file
	for idx0 in range(len(renamings)):
		for idx1 in range(idx0, len(renamings)):
			if idx0==idx1:
				continue
			if renamings[idx0][1]==renamings[idx1][0]:
				err('%s: renaming "%s" -> "%s" would collide with "%s"\n' %
					(prg, renamings[idx0][0], renamings[idx0][1], renamings[idx1][0]))
				return False

	# check if renamed files collide with existing files
	for name, newName in renamings:
		if os.path.exists(newName):
			err('%s: rename collision with existing file/directory: "%s" -> "%s"\n' %
				(prg, name, newName))
			return False
	
	return True


def createDirectories(pathName):
	if not pathName:
		return

	if not os.path.exists(pathName):
		if os.path.dirname(pathName)!='':
			dirName=os.path.dirname(pathName)
			createDirectories(dirName)
		else:
			os.mkdir(pathName)


if __name__=='__main__':
	sys.exit(main(sys.argv[1:]))
