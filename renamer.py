#! env python

import re, glob, sys, os, os.path

out=sys.stdout.write
err=sys.stderr.write
prg=os.path.basename(sys.argv[0])



def main(args):
	if len(args)<3:
		err('%s: v0.3.3 - A concoction by Andre Jonsson (2004-10-29)\n' % prg)
		err('Usage [-q] <find-regex> <replace> <files & dirs...>\n')
		err('   -q     By wewwy, wewwy quiet  (and rename without question)\n')
		sys.exit(0)

	quiet=False
	if args[0]=='-q':
		quiet=True
		args=args[1:]

	try:
		pattern=re.compile(args[0])
	except Exception, msg:
		err('%s: could not compile regular expression: %s\n%s' % (prg, args[0], msg))
		sys.exit(1)

	replace=args[1]
	files=args[2:]

	fileList={}
	for f in files:
		names=glob.glob(f)
		for n in names:
			fileList[n]=1

	fileList=fileList.keys()
	fileList.sort()

	renamings=[]
	for name in fileList:
		newName=strReplace(pattern, replace, name)
		renamings.append((name, newName))

	renamings=checkCollisions(renamings)
	if not renamings:
		sys.exit(1)

	if not quiet:
		for name, newName in renamings:
			out('  rename:  "%s" -> "%s"\n' % (name, newName))

	if not quiet:
		try:
			answer=raw_input('** Continue with rename? [Y/n] ').strip()
			if answer=='n':
				sys.exit(0)
		except SystemExit, msg:
			sys.exit(0)
		except:
			out('aborted\n')
			sys.exit(0)

	for rename in renamings:
		name, newName = rename
		try:
			createDirectories(os.path.dirname(newName))
			os.rename(name, newName)
		except Exception, msg:
			err('%s: renaming "%s" to "%s" failed: %s\n' % (prg, name, newName, msg))


def strReplace(pattern, replace, name):
	idx=0
	while 1:
		m=pattern.search(name[idx:])
		if not m:
			return name
		
		name=name[0:idx+m.start()] + m.expand(replace) + name[idx+m.end():]
		idx=m.start()+len(replace)

	return name


def checkCollisions(renamings):
	# check empty names
	for name, newName in renamings:
		if not newName:
			err('%s: can not rename to empty name: "%s" -> "%s"\n' %
				(prg, name, newName))
			return False

	# check for no-op rename
	newRenamings=[]
	for name, newName in renamings:
		if newName != name:
			newRenamings.append((name, newName))
	renamings=newRenamings
	
	# check if renamed files collide
	for idx0 in range(len(renamings)):
		for idx1 in range(len(renamings)):
			if idx0==idx1:
				continue
			if renamings[idx0][1]==renamings[idx1][1]:
				err('%s: rename collision: "%s" -> "%s"\n' %
					(prg, renamings[idx0][0], renamings[idx0][1]))
				err('%s: rename collision: "%s" -> "%s"\n' %
					(prg, renamings[idx1][0], renamings[idx1][1]))
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
			err('%s: rename collision "%s" -> "%s" file/directory exists.\n' %
				(prg, name, newName))
			return False
	
	return renamings


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
	main(sys.argv[1:])
