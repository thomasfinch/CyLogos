// function keyword is messed up

%hook NSObject

func,tion description() {
	return %orig + " (of doom)";
}

%end