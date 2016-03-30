%hook SpringBoard

function powerDownCanceled_(arg) {
	NSLog(@"Power down cancelled (from cycript) %@", arg);
	return %orig;
}

%end