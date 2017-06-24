from xmlnode import *

# XML Nodes for `.mmp` files

PPQN = 48 # Pulses per quarter note. Can this be configured???

class Note(XmlNode):
    _attributes = {
        "pan": AT_INT(0),
        "key": AT_INT(60),
        "vol": AT_INT(100),
        "pos": AT_INT(100),
        "len": AT_INT(100),
    }

class Pattern(XmlNode):
    _attributes = {
        "steps": AT_INT(16),
        "muted": AT_BOOL(False),
        "type": AT_INT(1),
        "name": AT_STRING("Pattern"),
        "pos": AT_INT(0),
        "len": AT_INT(100),
    }
    _children = [Note]

    @property
    def beat_len(self):
        return self.len / float(PPQN)
    
    @beat_len.setter
    def beat_len(self, l):
        self.len = int(round(l * PPQN))

    class HOLD(object):
        pass

    def set_melody(self, notes, note_beat_len=1):
        note_len_pulse = int(round(note_beat_len * PPQN))
        self.notes = []
        for offset, pitch in enumerate(notes):
            if pitch is None:
                continue
            if pitch is self.HOLD:
                self.notes[-1].len += note_len_pulse
                continue

            note = Note()
            note.pan = 0
            note.key = pitch
            note.vol = 100
            note.pos = note_len_pulse * offset
            note.len = note_len_pulse
            self.notes.append(note)
        self.len = len(notes) * note_len_pulse

    def __repr__(self):
        return "<Pattern: len={}b>".format(self.len)

    def shift_pitch(self, shift_deg):
        for note in self.notes:
            note.key += shift_deg

class Time(XmlNode):
    _attributes = {
        "value": AT_FLOAT(0),
        "pos": AT_INT(0),
    }

class Object(XmlNode):
    _attributes = {
        "id": AT_INT(0),
    }

class AutomationTrack(XmlNode):
    _name = "automation_track"

class AutomationPattern(XmlNode):
    _name = "automation_pattern"
    _attributes = {
        "tens": AT_INT(1),
        "mute": AT_BOOL(False),
        "prog": AT_INT(0),
        "name": AT_STRING("Automation Pattern"),
        "pos": AT_INT(100),
        "len": AT_INT(200),
    }
    _children = ["time", "object"]

class FxChain(XmlNode):
    _name = "fx_chain"
    _attributes = {
        "numofeffects": AT_INT(0),
        "enabled": AT_BOOL(False),
    }

class MidiPort(XmlNode):
    _name = "midi_port"
    _attributes = {
        "basevelocity": AT_INT(63),
        "fixedinputvelocity": AT_INT(-1),
        "fixedoutputnote": AT_INT(-1),
        "fixedoutputvelocity": AT_INT(-1),
        "inputchannel": AT_INT(0),
        "inputcontroller": AT_INT(0),
        "outputchannel": AT_INT(1),
        "outputcontroller": AT_INT(0),
        "outputprogram": AT_INT(1),
        "readable": AT_BOOL(False),
        "writable": AT_BOOL(False),
    }

class Arppegiator(XmlNode):
    _attributes = {
        "arptime": AT_INT(100),
        "arprange": AT_INT(1),
        "arptime_denominator": AT_INT(4),
        "arptime_numerator": AT_INT(4),
        "syncmode": AT_INT(0),
        "arpmode": AT_INT(0),
        "arp-enabled": AT_BOOL(False),
        "arp": AT_INT(0),
        "arpdir": AT_INT(0),
        "arpgate": AT_INT(100),
    }

class ChordCreator(XmlNode):
    _name = "chord_creator"
    _attributes = {
        "chord": AT_INT(0),
        "chordrange": AT_INT(1),
        "chord-enabled": AT_BOOL(0),
    }

class ElData(XmlNode):
    _attributes = {
        "freq": AT_FLOAT(0.5),
        "ftype": AT_INT(0),
        "fcut": AT_INT(14000),
        "fwet": AT_INT(0),
    }
    _children = ["elvol", "elcut", "elres"]

class ElVol(XmlNode):
    _attributes = {
        "amt": AT_FLOAT(0),
        "att": AT_FLOAT(0),
        "ctlenvamt": AT_FLOAT(0),
        "dec": AT_FLOAT(0.5),
        "hold": AT_FLOAT(0.5),
        "lamt": AT_FLOAT(0),
        "latt": AT_FLOAT(0),
        "lpdel": AT_FLOAT(0),
        "lshp": AT_FLOAT(0),
        "lspd": AT_FLOAT(0.1),
        "lspd_denominator": AT_INT(4),
        "lspd_numerator": AT_INT(4),
        "pdel": AT_FLOAT(0),
        "rel": AT_FLOAT(0.1),
        "sustain": AT_FLOAT(0.5),
        "syncmode": AT_INT(0),
        "userwavefile": AT_STRING(""),
        "x100": AT_BOOL(False),
    }

class ElCut(ElVol):
    pass

class ElRes(ElVol):
    pass

class Instrument(XmlNode):
    _attributes = {
        "name": AT_STRING("instrument"),
    }
    _children = ["organic", "tripleoscillator"] # TODO: Make generic

class Organic(XmlNode):
    pass #XXX

class TripleOscillator(XmlNode):
    pass #XXX

class InstrumentTrack(XmlNode):
    _name = "instrument_track"
    _attributes = {
        "pan": AT_INT(0),
        "fxch": AT_INT(0),
        "pitchrange": AT_INT(1),
        "pitch": AT_INT(0),
        "basenote": AT_INT(57),
        "vol": AT_INT(100),
    }
    _children = ["instrument", "eldata", "chord_creator", "arppegiator", "midi_port", "fx_chain", "pattern"]

class SampleTrack(XmlNode):
    _name = "sample_track"
    _attributes = {
        "vol": AT_INT(100),
    }
    _children = ["fx_chain"]

class Track(XmlNode):
    _attributes = {
        "name": AT_STRING("Track"),
        "muted": AT_BOOL(False),
        "solo": AT_BOOL(False),
        "type": AT_INT(0),
    }
    _children = ["bb_track", "instrument_track", "sample_track", "automation_track", "automation_pattern", "pattern"]

    def load_extra(self, *args, **kwargs):
        self.path = []
        p = self.parent
        while p is not None:
            if p._name == "track":
                self.path.insert(0, p.name)
            elif p._name == "track_container":
                self.path.insert(0, p.type)
            p = p.parent

    @property
    def full_name(self):
        return "::".join(list(self.path) + [self.name])

    def __repr__(self):
        return "<Track: {}>".format(self.full_name)

class TrackContainer(XmlNode):
    _name = "track_container"
    _attributes = dict({
        "type": AT_STRING("song"),
    }, **VIEW_ATTRIBUTES)
    _children = ["track"]

class BBTrack(XmlNode):
    _name = "bb_track"
    _children = ["track_container", "track"]

class FxMixer(XmlNode):
    _name = "fx_mixer"
    _attributes = VIEW_ATTRIBUTES
    _children = ["fx_channel"]

class FxChannel(XmlNode):
    _name = "fx_channel"
    _attributes = {
        "num": AT_INT(0),
        "muted": AT_BOOL(False),
        "volume": AT_FLOAT(1),
        "name": AT_STRING("Master"),
    }
    _children = ["fx_chain"]

class ControllerRackView(XmlNode):
    _name = "controller_rack_view"
    _tag = "ControllerRackView"
    _attributes = VIEW_ATTRIBUTES

class PianoRoll(XmlNode):
    _name = "piano_roll"
    _attributes = VIEW_ATTRIBUTES

class AutomationEditor(XmlNode):
    _name = "automation_editor"
    _attributes = VIEW_ATTRIBUTES

class ProjectNotes(XmlNode):
    _name = "project_notes"
    _attributes = VIEW_ATTRIBUTES

class Timeline(XmlNode):
    _attributes = {
        "lp1pos": AT_INT(0),
        "lp0pos": AT_INT(0),
        "lpstate": AT_INT(0),
    }

class Controllers(XmlNode):
    pass

class LmmsProject(XmlNode):
    _name = "project"
    _tag = "lmms-project"
    _children = ["head", "song"]
    _attributes = {
        "version": AT_STRING("1.0"),
        "creator": AT_STRING("LMMS"),
        "creatorversion": AT_STRING("1.1.3"),
        "type": AT_STRING("song"),
    }

class LmmsProjectHead(XmlNode):
    _name = "head"
    _tag = "head"
    _attributes = {
        "timesig_numerator": AT_INT(4),
        "timesig_denominator": AT_INT(4),
        "mastervol": AT_INT(100),
        "masterpitch": AT_INT(0),
        "bpm": AT_INT(140),
    }

class Song(XmlNode):
    _children = ["track_container", "track", "fx_mixer", "controller_rack_view", "piano_roll", "automation_editor", "project_notes", "timeline", "controllers"]

def load_project(file_or_filename):
    if not hasattr(file_or_filename, "read"):
        file_or_filename = open(file_or_filename, "r")
    with file_or_filename as f:
        tree = ET.parse(f)
    return LmmsProject.load(tree.getroot())

def save_project(project, file_or_filename):
    project_el = project.dump()
    tree = ET.ElementTree(project_el)
    if not hasattr(file_or_filename, "write"):
        file_or_filename = open(file_or_filename, "w")
    with file_or_filename as f:
        f.write('<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n')
        tree.write(f, xml_declaration=False)
