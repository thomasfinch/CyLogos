%hook SpringBoard

function handleMenuDoubleTap() {
	var alert = [[UIAlertView alloc] initWithTitle:'Double Click' message:'You double clicked the home button.' delegate:nil cancelButtonTitle:'Ok' otherButtonTitles:nil];
	[alert show];
}

%end