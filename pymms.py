import mms_xml
import util

PPQN = 48 # Pulses per quarter note. Can this be configured???

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
        if xml is None:
            xml = mms_xml.Track()
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
    def patterns(self):
        return [Pattern(p) for p in self.xml.patterns]

    @patterns.setter
    def patterns(self, ps):
        self.xml.patterns = [p.xml for p in ps]
    
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

class Pattern(LmmsObject):
    def __init__(self, xml=None):
        if xml is None:
            xml = mms_xml.Pattern()
        self.xml = xml

    @property
    def len(self):
        return self.xml.len / float(PPQN)
    
    @len.setter
    def len(self, l):
        self.xml.len = int(round(l * PPQN))

    class HOLD(object):
        pass

    def set_melody(self, notes, note_len=0.25):
        note_len_pulse = int(round(note_len * PPQN * 4))
        self.xml.notes = []
        for offset, note in enumerate(notes):
            if note is None:
                continue
            if note is self.HOLD:
                self.xml.notes[-1].len += note_len_pulse
                continue

            xml_note = mms_xml.Note()
            xml_note.pan = 0
            xml_note.key = note
            xml_note.vol = 100
            xml_note.pos = note_len_pulse * offset
            xml_note.len = note_len_pulse
            self.xml.notes.append(xml_note)
        self.len = len(notes) * note_len

    def __repr__(self):
        return "<Pattern: len={}b>".format(self.len)

    def shift_pitch(self, shift_deg):
        for note in self.xml.notes:
            note.key += shift_deg

UNISON = [65, 75, Pattern.HOLD, 72, 67, 67, 68, Pattern.HOLD, 65, 70, 72, 70, 65, 65, Pattern.HOLD, Pattern.HOLD, 65, 75, Pattern.HOLD, 72, 67, 67, 68, 65, 72, 75, Pattern.HOLD, 72, 77, Pattern.HOLD, None, None]

def test_render():
    with Project("test.mmp") as project:
        print project.tracks.keys()
        melody = project.tracks["song::Organic"].patterns[1]
        melody.set_melody(UNISON)
        #melody.shift_pitch(12)
        
        m2 = Pattern()
        m2.set_melody(UNISON)
        m2.shift_pitch(-12)
        project.tracks["song::TripleOscillator"].patterns = [m2]
        project.render('test.wav')

if __name__ == "__main__":
    test_render()
