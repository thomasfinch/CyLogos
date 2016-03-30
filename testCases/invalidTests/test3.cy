//Test nested %hooks

%hook NSObject

function declaration() {
	return 'testing!';
}

%hook UIView

%end