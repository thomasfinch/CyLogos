// Example from the cycript manual, in logos

%hook NSObject

function description() {
	return %orig + " (of doom)";
}

%end

printf('%s\n', [[[[NSObject alloc] init] description] UTF8String]);