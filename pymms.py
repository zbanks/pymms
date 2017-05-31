import mms_xml

def test_load():
    project = mms_xml.load_project("/home/zbanks/lmms/projects/test.mmp")
    mms_xml.save_project(project, "/dev/stdout")

if __name__ == "__main__":
    test_load()
