#!/usr/bin/python
import sys, string, re

hookRegEx = re.compile(r'%hook\s+(\w+)\s*')
functionRegEx = re.compile(r'\s*function\s+([\w|:]+)\s*\(([\w|,|\s]*)\)', re.DOTALL)

def fatalError(message):
	print 'Error: ' + message
	exit(1)

def assertValidKeyword(keyword, errorMsg, extraChars=[]):
	return
	# if not all(c in string.ascii_letters+string.digits+''.join(extraChars) for c in keyword):
	# 	fatalError(errorMsg)

def lineIsHookStart(line):
	return line.strip()[:5].lower() == '%hook'

def lineIsHookEnd(line):
	return line.strip().lower() == '%end'

def getClassNameFromHook(line):
	match = hookRegEx.search(line)
	if match is None:
		fatalError('Incorrect hook syntax: ' + line)

	className = match.groups()[0]
	assertValidKeyword(className, 'Invalid class name in hook: ' + line)

	return className

def processOrig(line, functionArgs, origMethodName):
	# No %orig calls to process
	if '%orig' not in line:
		return line

	# Process all %orig directives, ignoring them if they're inside string literals
	inDoubleQuoteString = False
	inSingleQuoteString = False
	for index, char in enumerate(line):
		if char == '"' and line[index-1] != '\\':
			inDoubleQuoteString = not inDoubleQuoteString
		elif char == '\'' and line[index-1] != '\\':
			inSingleQuoteString = not inSingleQuoteString

		# Found a valid %orig not in a string literal, process it
		if line[index:index+5] == '%orig' and not inDoubleQuoteString and not inSingleQuoteString:
			# Check for manual arguments to %orig
			origArguments = ''
			temp = line[index+5:].lstrip()
			if temp[0] == '(':
				origArguments = temp[1:temp.find(')')].strip()

			origCall = '->call(this)'
			lineEnd = line[index+5:]
			if len(origArguments) > 0:
				origCall = '->call(this, ' + origArguments + ')'
				lineEnd = line[line.find(')', index+5)+1:]
			elif len(functionArgs) > 0:
				origCall = '->call(this, ' + functionArgs + ')'
			line = line[:index] + origMethodName + origCall + lineEnd

	return line

def parseFunctions(lines):
	parsedFunctions = []

	# Join lines into one string
	line = '\n'.join(lines).rstrip()

	match = functionRegEx.search(line)
	while match is not None:
		# Get the body of the function (unfortunately can't do this with a regex)
		line = line[match.end():]
		line = line[line.find('{')+1:]
		bracketDepth = 1
		bodyEndIndex = 0
		for index, char in enumerate(line):
			if char == '{':
				bracketDepth += 1
			elif char == '}':
				bracketDepth -= 1

			if bracketDepth == 0:
				bodyEndIndex = index
				break

		functionBody = line[:bodyEndIndex]
		functionName, arguments = match.groups()
		parsedFunctions.append((functionName, arguments, functionBody))

		line = line[bodyEndIndex+1:]
		match = functionRegEx.search(line)

	if len(line.strip()) > 0:
		fatalError('Only functions are allowed in hooks: ' + line)

	return parsedFunctions

def processHook(lines):
	processedHookLines = []
	className = getClassNameFromHook(lines[0])
	lines = lines[1:-1] # remove %hook and %end lines

	funcs = parseFunctions(lines)

	for functionTuple in funcs:
		functionName = functionTuple[0]
		arguments = functionTuple[1]
		functionBody = functionTuple[2]

		# Create a variable for the old method implementation
		oldMethodName = className + '_' + functionName.replace(':', '_') + '_orig'
		processedHookLines.append('var ' + oldMethodName + ' = {};')

		processedHookLines.append('MS.hookMessage(' + className + ', @selector(' + functionName.replace('_', ':') + '), function(' + arguments + ') {')

		for functionBodyLine in functionBody.split('\n'):
			if len(functionBodyLine) > 0:
				processedHookLines.append(processOrig(functionBodyLine, arguments, oldMethodName))

		processedHookLines.append('}, ' + oldMethodName + ')')

	return processedHookLines

def main():
	if len(sys.argv) < 2:
		fatalError('Need filename argument.')

	inHook = False
	processedLines = ['@import com.saurik.substrate.MS', '@import org.cycript.NSLog']
	hookLines = []

	file = open(sys.argv[1], 'r')
	for lineNum, line in enumerate(file):

		# Skip empty lines
		if len(line.strip()) == 0:
			continue

		line = line.rstrip()

		# Handle %hook
		if lineIsHookStart(line):
			if not inHook:
				inHook = True
			else:
				fatalError('Cannot nest %hook\'s (line ' + str(lineNum+1) + ').')

		# Process each line
		if inHook:
			hookLines.append(line)
		else:
			processedLines.append(line)

		# Handle %end
		if lineIsHookEnd(line):
			if inHook:
				inHook = False
				processedLines += processHook(hookLines)
				hookLines = []
			else:
				fatalError('Found a %end without finding a %hook first (line ' + str(lineNum+1) + ').')

	if inHook:
		fatalError('Found a %hook without a matching %end.')

	file.close()

	for line in processedLines:
		print line

if __name__ == "__main__":
	main()