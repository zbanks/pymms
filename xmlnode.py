from xml.etree import ElementTree as ET

__all__ = ("AT_BOOL", "AT_INT", "AT_FLOAT", "AT_STRING", "VIEW_ATTRIBUTES", "XmlNode", "ET")

ident = lambda x: x
AT_BOOL = lambda x: (x, lambda x: bool(int(x)), lambda x: str(int(x)))
AT_INT = lambda x: (x, int, str)
AT_FLOAT = lambda x: (x, float, str)
AT_STRING = lambda x: (x, ident, ident)

VIEW_ATTRIBUTES = {
    "width": AT_INT(600),
    "height": AT_INT(400),
    "x": AT_INT(10),
    "y": AT_INT(10),
    "maximized": AT_BOOL(False),
    "minimized": AT_BOOL(False),
    "visible": AT_BOOL(True),
}

format_attr = lambda x: x.replace("-", "_")
unformat_attr = lambda x: x.replace("_", "-")

class XmlNodeMeta(type):
    registry = {}
    def __new__(cls, name, parents, dct):
        if dct.get("_tag") is None:
            dct["_tag"] = name.lower()
        if dct.get("_name") is None:
            dct["_name"] = name.lower()
        if dct.get("_name_plural") is None:
            dct["_name_plural"] = dct["_name"] + "s"

        for child_name in dct.get("_children", []):
            if not isinstance(child_name, str):
                child_name = child_name._name
            def _add_child(_self, *args, **kwargs):
                child_cls = XmlNodeMeta.registry[child_name]
                new_child = child_cls(*args, **kwargs)
                children = getattr(self, child_cls._name_plural)
                children.append(new_child)
                return new_child
            dct["add_" + child_name] = _add_child

        ret = super(XmlNodeMeta, cls).__new__(cls, name, parents, dct)
        XmlNodeMeta.registry[ret._name] = ret
        return ret

class XmlNode(object):
    __metaclass__ = XmlNodeMeta
    #_name = "tag"
    #_name_plural = "tags"
    #_tag = "tag"
    _children = []
    _attributes = {}

    def __init__(self, **kwargs):
        self.extra_attrib = {}

        for kw, value in kwargs.items():
            if kw in self._attributes:
                setattr(self, kw, value)

    @classmethod
    def load(cls, el, parent=None):
        self = cls()
        if el.tag != cls._tag:
            raise Exception("Got tag '{}' expected '{}' for {}"
                    .format(el.tag, cls._tag, cls.__name__))

        self.parent = parent
        if parent is not None:
            self.nodes = parent.nodes
        else:
            self.nodes = {}
        if cls._name_plural not in self.nodes:
            self.nodes[cls._name_plural] = []
        self.nodes[cls._name_plural].append(self)

        for attr, (default, conv_fn, _) in cls._attributes.items():
            try:
                value = conv_fn(el.attrib.pop(attr))
            except KeyError, ValueError:
                value = default
            setattr(self, format_attr(attr), value)
        self.extra_attrib = el.attrib

        for child_node in cls._children:
            if isinstance(child_node, str):
                child_node = XmlNodeMeta.registry[child_node]
            children = []
            children_els = el.findall(child_node._tag)
            if children_els is not None:
                for child_el in children_els:
                    children.append(child_node.load(child_el, parent=self))
            setattr(self, child_node._name_plural, children)

        cls.load_extra(self, el)
        return self

    @classmethod
    def load_extra(cls, self, el):
        pass

    def dump(self):
        attributes = self.extra_attrib
        for attr, (default, _, conv_fn) in self._attributes.items():
            try:
                attributes[attr] = conv_fn(getattr(self, unformat_attr(attr), default))
            except ValueError:
                attributes[attr] = conv_fn(default)

        el = ET.Element(self._tag, attributes)

        for child_node in self._children:
            if isinstance(child_node, str):
                child_node = XmlNodeMeta.registry[child_node]
            children = getattr(self, child_node._name_plural)
            for child in children:
                el.append(child.dump())

        el = self.dump_extra(el)
        return el

    def dump_extra(self, el):
        return el

