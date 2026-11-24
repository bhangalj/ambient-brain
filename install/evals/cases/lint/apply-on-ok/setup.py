import runpy, os
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_lint_plant.py"))
# Another session's in-flight work, left after the plant commit.
with open("people/bob-stone.md", "a") as f:
    f.write("\nDRAFT-IN-FLIGHT: another session is still editing this line.\n")
