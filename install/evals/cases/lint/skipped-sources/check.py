# Undistilled sources are flagged, except the ones listed in SKIPPED.md.
from evalkit import *
o = out()
expect("333_globex-discovery" in o, "lint missed the undistilled Globex transcript")
expect(not flagged("222_it-huddle"), "lint flagged a source listed in SKIPPED.md")
expect(vault_unchanged(), "lint changed the vault without an OK")
done()
