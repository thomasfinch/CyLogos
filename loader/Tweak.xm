#import <Foundation/Foundation.h>
#import <stdio.h>

// NSString* const cyLogosDir = @"/Library/CyLogos";
NSString* const tweaksDir = @"/Library/CyLogos/Tweaks";
NSString* const preprocessedTempFile = @"/Library/CyLogos/tmp";

NSString* runCommand(NSString *command, int* returnValue) {
	FILE *fp = popen([command UTF8String], "r");
	if (fp == NULL) {
		*returnValue = -1;
		return @"Error running command.";
	}

	NSFileHandle *fileHandle = [[NSFileHandle alloc] initWithFileDescriptor:fileno(fp)];
	NSString *output = [[NSString alloc] initWithData:[fileHandle availableData] encoding:NSUTF8StringEncoding];

	*returnValue = pclose(fp);
	return output;
}

void subscribeToFSNotifications(NSString* file, void(^changeBlock)(unsigned long)) {
	__block int fileDescriptor = open([file UTF8String], O_EVTONLY);
	dispatch_queue_t defaultQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
	dispatch_source_t source = dispatch_source_create(DISPATCH_SOURCE_TYPE_VNODE, fileDescriptor, DISPATCH_VNODE_DELETE | DISPATCH_VNODE_WRITE, defaultQueue);
	
	dispatch_source_set_event_handler(source, ^{
		unsigned long eventTypes = dispatch_source_get_data(source);
		changeBlock(eventTypes);
	});
	
	dispatch_source_set_cancel_handler(source, ^{
		close(fileDescriptor);
		fileDescriptor = 0;
	});
	
	dispatch_resume(source);
}

void injectScript(NSString *fileName) {
	NSLog(@"CyLogos loader: Injecting %@", fileName);

	int returnValue = 0;
	NSString *output = @"";

	//Preprocess with CyLogos
	output = runCommand([NSString stringWithFormat:@"cylogos %@/%@ > %@", tweaksDir, fileName, preprocessedTempFile], &returnValue);
	if (returnValue != 0) {
		output = runCommand([NSString stringWithFormat:@"cat %@", preprocessedTempFile], &returnValue);
		NSLog(@"CyLogos loader: Error preprocessing %@: %@", fileName, output);
		return;
	}

	//Compile with Cycript
	NSString *tempFile = runCommand(@"mktemp -t cylogos.XXXXX", &returnValue);
	if (returnValue != 0) {
		NSLog(@"CyLogos loader: Error obtaining temporary file.");
		return;
	}
	output = runCommand([NSString stringWithFormat:@"cycript -c %@ > %@", preprocessedTempFile, tempFile], &returnValue);
	if (returnValue != 0) {
		output = runCommand([NSString stringWithFormat:@"cat %@", tempFile], &returnValue);
		NSLog(@"CyLogos loader: Error compiling %@: %@", fileName, output);
		return;
	}

	//Inject with Cycript
	NSString *appName = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleName"];
	output = runCommand([NSString stringWithFormat:@"cycript -p %@ %@", appName, tempFile], &returnValue); //This almost always segfaults cycript (at least on iOS 6), idk why. Script is still injected though

	NSLog(@"CyLogos loader: Successfully injected %@", fileName);
}

%ctor {
	NSLog(@"CyLogos loader is loaded! (bundle ID: %@)", [[NSBundle mainBundle] bundleIdentifier]);

	// subscribeToFSNotifications(tweaksDir, ^void(unsigned long eventTypes) {
	// 	NSLog(@"STUFF CHANGED IN TWEAKS DIR");
	// 	if (eventTypes & DISPATCH_VNODE_DELETE)
	// 		NSLog(@"deleted");
	// 	if (eventTypes & DISPATCH_VNODE_WRITE)
	// 		NSLog(@"modified");

	// 	loadScripts();
	// });

	// CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(), NULL, (CFNotificationCallback)loadScripts, CFSTR("me.thomasfinch.cylogos-reload"), NULL, CFNotificationSuspensionBehaviorDeliverImmediately);

	NSArray* cyFiles = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:tweaksDir error:NULL];
	for (NSString* file in cyFiles) {
		// To do: Check the filter on each file to make sure it matches the current process bundle ID
		injectScript(file);
	}
}

%dtor {
	NSLog(@"CYLOGOS LOADER IS DESTRUCTING!!!! ASDFASDFASDFASDFASDFASDFASDFDS");
	//Remove owned temp files here. Unfortunately this isn't called when springboard is killed forcibly.
}
