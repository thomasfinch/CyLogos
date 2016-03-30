# CyLogos

A preprocessor + loader that allows use of Logos syntax with Cycript. Simply drop .cy files in `/Library/CyLogos/Tweaks` to have them automatically preprocessed and loaded into SpringBoard. Only %hook, %end, and %orig are supported currently.

Check out [Cycript.org](http://www.cycript.org) and [the iPhone Dev Wiki Logos page](http://iphonedevwiki.net/index.php/Logos) for more information on Cycript and Logos.

### Example
Example file before preprocessing (based on [this cycript demo](http://www.cycript.org/manual/#6635fc86-3c73-4176-b0b0-75dd3aa99ce3)):
```javascript
%hook NSObject

function description() {
	return %orig + " (of doom)";
}

%end
```

Preprocessed:
```javascript
var oldm = {};
MS.hookMessage(NSObject, @selector(description), function() {
    return oldm->call(this) + " (of doom)";
}, oldm)
```

### How to use (specifics)
There are a few basic assumptions for syntax:
  1. Each %hook and %end directive is on a line by itself.
  2. Function names within %hook blocks match the objective-C selector that they want to hook.

This means that to hook SBApplicationController's method `- (void)_sendInstalledAppsDidChangeNotification:(id)arg1 removed:(id)arg2 modified:(id)arg3`, you would write the following script:
```javascript
%hook SBApplicationController

function _sendInstalledAppsDidChangeNotification:removed:modified:(arg1, arg2, arg3) {
  //Do stuff here
  %orig;
}

%end
```

To load the above script, install the loader tweak, save the script as a .cy file in `/Library/CyLogos/Tweaks` and run `killall SpringBoard` on your device.

The syntax rules are pretty much the same as the actual Logos (no %hook nesting, %orig can be called with or without arguments, etc.). It's good practice to end each statement with a semicolon even though Cycript doesn't require it because it can sometimes mess up the Cycript parser if they're left out.

### FAQ

__What can I use this for?__

This could be helpful for tweak developers to quickly prototype tweaks or for beginners to learn Logos syntax.

__How do I use it?__

Write a tweak in cycript + logos syntax, drop it in `/Library/CyLogos/Tweaks` with the loader tweak installed, restart SpringBoard, and watch the system log for preprocessor or Cycript errors. See the examples folder for a few example tweaks (tested on iOS 6).

__When will \_\_\_\_ be supported?__

It depends. Some things like C function hooking are on the to-do list (see `To do.txt`), but others like support for hooking daemons aren't. For use cases beyond basic tweaks or for more powerful objective-C features you should use [Theos](https://github.com/theos/theos).

__Why is the preprocessor written in Python/why is \_\_\_\_ kind of hacky?__

A lot of this is kind of experimental/just me trying things out. Python is easy for prototyping and it conveniently runs on jailbroken iOS. I'll probably change the language used eventually. If you have a better way to do something, let me know!
