//Test %hook without a %end

%hook NSObject

function declaration() {
	return 'testing!';
}