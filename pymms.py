import mms_xml
import util

class LmmsObject(object):
    pass

class Project(LmmsObject):
    def __init__(self, filename=None):
        assert filename is not None, NotImplementedError("unable to create from scratch yet")
        self.filename = filename
        self.xml = mms_xml.load_project(filename)
        assert len(self.xml.songs) == 1, NotImplementedError("project must have exactly 1 song")
        self.xml_song = self.xml.songs[0]
    
    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        if filename is None:
            raise ValueError("Must specify filename")
        mms_xml.save_project(self.xml, filename)
        util.xmllint(filename)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.save(self.filename + ".out")
        return False

    def render(self, output_wav=None):
        if output_wav is None:
            output_wav = self.filename + ".wav"
        tmp_file = self.filename + "-render.mmp"
        self.save(tmp_file)
        util.lmms_render(tmp_file, output_wav)
        return output_wav
    
    def __repr__(self):
        return "<LmmsProject: {}>".format(filename)

    @property
    def tracks(self):
        tracks = [Track(t) for t in self.xml.nodes["tracks"]]
        return {t.full_name: t for t in tracks}

class Track(LmmsObject):
    def __init__(self, xml=None):
        assert xml is not None, NotImplementedError("unable to create from scratch yet")
        self.xml = xml
        self.path = []
        p = xml.parent
        while p is not None:
            if p._name == "track":
                self.path.insert(0, p.name)
            elif p._name == "track_container":
                self.path.insert(0, p.type)
            p = p.parent
    
    @property
    def name(self):
        return self.xml.name

    @name.setter
    def name(self, n):
        self.xml.name = n

    @property
    def full_name(self):
        return "::".join(list(self.path) + [self.name])

    def __repr__(self):
        return "<Track: {}>".format(self.full_name)

def test_render():
    with Project("test.mmp") as project:
        print project.tracks
        project.render('test.wav')

if __name__ == "__main__":
    test_render()
