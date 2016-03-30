// General test case (tests functions with arguments)

%hook NSArray

function writeToFile_atomically_(file, atomically) {
	printf('Writing to file atomically!\n');
	printf('Filename: %s\n', [file UTF8String]);
	printf('Atomically: %d\n', atomically);
	return YES;
}

%end


var arr = [[NSArray alloc] init];
[arr writeToFile:@"testFile" atomically:YES];