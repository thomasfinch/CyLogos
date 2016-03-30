// Idk just a general valid test case

%hook NSObject

function testing() {
	printf("testing\n")
}

function asdf(arg1, arg2, thirdArg) {
	var a = 5
	var b = 3 * 10
	if (a >= 5) {
		a++
	}
	return a + b
}

%end