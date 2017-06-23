import subprocess

def lmms_render(mms_xml_file, output_wav):
    subprocess.check_call([
        "lmms",
        "--render", mms_xml_file,
        "--output", output_wav,
    ])

def xmllint(filename):
    with open(filename, "r") as f:
        data = f.read()
    with open(filename, "w") as f:
        p = subprocess.Popen(["xmllint", "--format", "/dev/stdin"], stdin=subprocess.PIPE, stdout=f)
        p.stdin.write(data)
        p.stdin.close()
        if p.wait() != 0:
            raise OSError("xmllint --format returned {}".format(p.returncode))
