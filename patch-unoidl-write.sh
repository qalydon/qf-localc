# List dependencies
# otool -l /Users/dhocker/LibreOffice26.2_SDK/bin/unoidl-write

# Patch unoidl-write dylib references. This will break the code signing.
install_name_tool -change "@__VIA_LIBRARY_PATH__/libunoidllo.dylib.3" "/Applications/LibreOffice.app/Contents/Frameworks/libunoidllo.dylib.3" /Users/dhocker/LibreOffice26.2_SDK/bin/unoidl-write
install_name_tool -change "@__VIA_LIBRARY_PATH__/libuno_salhelpergcc3.dylib.3" "/Applications/LibreOffice.app/Contents/Frameworks/libuno_salhelpergcc3.dylib.3" /Users/dhocker/LibreOffice26.2_SDK/bin/unoidl-write
install_name_tool -change "@__VIA_LIBRARY_PATH__/libuno_sal.dylib.3" "/Applications/LibreOffice.app/Contents/Frameworks/libuno_sal.dylib.3" /Users/dhocker/LibreOffice26.2_SDK/bin/unoidl-write

# Force sign the changed executable
codesign --force -s - /Users/dhocker/LibreOffice26.2_SDK/bin/unoidl-write
