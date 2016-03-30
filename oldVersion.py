import sys, re, string

hookRegEx = re.compile(r'%hook\s+(\w+)\s*\n\s*(.*?)\n\s*%end', re.DOTALL)
functionRegEx = re.compile(r'\s*function\s+([\w|:]+)\s*\(([\w|,|\s]*)\)', re.DOTALL)
origWithArgsRegEx = re.compile(r'%orig\s*\(([\w|,|\s]*)\)')

def fatalError(message):
	print 'Error: ' + message
	exit(1)

def processOrig(body, origMethodName, functionArgs):
	# Process all calls to %orig with arguments
	match = origWithArgsRegEx.search(body)
	while match is not None:
		arguments = match.groups()[0]
		body = body[:match.start()] + origMethodName + '->call(this, ' + arguments + ')' + body[match.end():]
		match = origWithArgsRegEx.search(body)

	# Process all calls to %orig without arguments
	while body.find('%orig') != -1:
		origIndex = body.find('%orig')
		body = body[:origIndex] + origMethodName + '->call(this)' + body[origIndex+5:]

	return body

def processFunction(regExMatch, hookedClass, functionBody):
	functionName, arguments = regExMatch.groups()

	# check that the number of :'s == number of function arguments

	origMethodName = hookedClass + '_' + functionName.replace(':', '_') + '_orig'
	functionBody = processOrig(functionBody, origMethodName, arguments)

	returnStr = 'var ' + origMethodName + ' = {};\n'
	returnStr += 'MS.hookMessage(' + hookedClass + ', @selector(' + functionName + '), function(' + arguments + ') {'
	returnStr += functionBody
	returnStr += '}, ' + origMethodName + ')\n\n'

	return returnStr

def processHook(regExMatch):
	hookedClass, hookBody = regExMatch.groups()

	# Check that hookBody doesn't contain any %hook's (can't be nested)
	if '%hook' in hookBody:
		fatalError('Cannot nest %hook\'s')

	processedStr = ''
	match = functionRegEx.search(hookBody)
	while match is not None:
		processedStr += hookBody[:match.start()]

		# Get the body of the function (unfortunately can't do this with a regex)
		hookBody = hookBody[match.end():]
		hookBody = hookBody[hookBody.find('{')+1:]
		bracketDepth = 1
		bodyEndIndex = 0
		for index, char in enumerate(hookBody):
			if char == '{':
				bracketDepth += 1
			elif char == '}':
				bracketDepth -= 1

			if bracketDepth == 0:
				bodyEndIndex = index
				break

		functionBody = hookBody[:bodyEndIndex]
		hookBody = hookBody[bodyEndIndex+1:]
		processedStr += processFunction(match, hookedClass, functionBody)
		match = functionRegEx.search(hookBody)

	return processedStr


def main():
	if len(sys.argv) < 2:
		fatalError('Need filename argument.')

	file = open(sys.argv[1], 'r')
	fileStr = file.read()

	# Find and process all %hook...%end blocks
	match = hookRegEx.search(fileStr)
	while match is not None:
		fileStr = fileStr[:match.start()] + processHook(match) + fileStr[match.end():]
		match = hookRegEx.search(fileStr)

	print fileStr

	# Check that there aren't any remaining %hook's or %end's, if so then there's a mismatch
	if fileStr.find('%hook') != -1:
		fatalError('Found %hook without a %end.')
	if '%end' in fileStr:
		fatalError('Found %end without a %hook.')

	fileStr = '@import com.saurik.substrate.MS\n@import org.cycript.NSLog\n\n' + fileStr

	print fileStr

if __name__ == "__main__":
	main()
