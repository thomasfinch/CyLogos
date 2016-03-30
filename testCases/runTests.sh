#!/bin/bash

passedAllTests=true

# Run all valid tests, make sure they return 0
for i in $(ls validTests); do
	python ../cylogos.py validTests/$i > /dev/null
	if [ $? -ne 0 ]
		then
		echo 'Valid test case failed:' $i
		passedAllTests=false
	fi
done

# Run all invalid tests, make sure they don't return 0
for i in $(ls invalidTests); do
	python ../cylogos.py invalidTests/$i > /dev/null
	if [ $? -eq 0 ]
		then
		echo 'Invalid test case failed:' $i
		passedAllTests=false
	fi
done


if [ "$passedAllTests" = true ] ; then
    echo 'All tests passed'
fi