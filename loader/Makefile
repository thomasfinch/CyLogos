TARGET_IPHONEOS_DEPLOYMENT_VERSION = 6.0

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = CyLogos
CyLogos_FILES = Tweak.xm

include $(THEOS_MAKE_PATH)/tweak.mk

before-package::
	cp -f ../cylogos.py layout/usr/bin/cylogos
	chmod +rx layout/usr/bin/cylogos

after-install::
	install.exec "killall -9 SpringBoard"
