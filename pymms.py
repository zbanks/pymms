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
        tracks = self.xml.nodes["tracks"]
        return {t.full_name: t for t in tracks}

HOLD = mms_xml.Pattern.HOLD
UNISON = [65, 75, HOLD, 72, 67, 67, 68, HOLD, 65, 70, 72, 70, 65, 65, HOLD, HOLD, 65, 75, HOLD, 72, 67, 67, 68, 65, 72, 75, HOLD, 72, 77, HOLD, None, None]

def test_render():
    with Project("test.mmp") as project:
        print project.tracks.keys()
        melody = project.tracks["song::Organic"].patterns[1]
        melody.set_melody(UNISON)
        #melody.shift_pitch(12)
        
        m2 = mms_xml.Pattern()
        m2.set_melody(UNISON)
        m2.shift_pitch(-12)
        project.tracks["song::TripleOscillator"].patterns = [m2]
        project.render('test.wav')

if __name__ == "__main__":
    test_render()
