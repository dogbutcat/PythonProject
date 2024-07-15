import plistlib

with open("Info.plist", "rb") as fp:
    info_plist = plistlib.load(fp)

file_icons = info_plist.get('CFBundleIcons',{})
alternate_icons = file_icons.get("CFBundleAlternateIcons",{})

max_range = 6573
new_alternate_icons = {}

for i in range(max_range):
    new_icon_name = 'ba{}'.format('%05d' % i)
    new_icon_entry = {
        "CFBundleIconFiles": [new_icon_name],
        "UIPrerenderedIcon": False,
    }
    new_alternate_icons[new_icon_name] = new_icon_entry

# print(dir(info_plist))
# print(info_plist)
# print(alternate_icons)

file_icons['CFBundleAlternateIcons'] = new_alternate_icons

with open('Info.plist', 'wb') as fp:
    plistlib.dump(info_plist, fp)