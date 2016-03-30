// Tests one line functions

%hook NSObject

function testing() {   printf("testing\n")    }

%end