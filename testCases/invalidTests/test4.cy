//Test dangling %end

%hook NSObject

function declaration() {
	return 'testing!';
}

%end

%end