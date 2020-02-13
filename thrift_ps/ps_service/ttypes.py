#
# Autogenerated by Thrift Compiler (0.13.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class Operation(object):
    PING = 1
    REGISTER = 2
    EXIST_MODEL = 3
    CAN_PULL = 4
    CAN_PUSH = 5
    PULL_MODEL = 6
    PUSH_GRAD = 7
    PUSH_UPDATE = 8

    _VALUES_TO_NAMES = {
        1: "PING",
        2: "REGISTER",
        3: "EXIST_MODEL",
        4: "CAN_PULL",
        5: "CAN_PUSH",
        6: "PULL_MODEL",
        7: "PUSH_GRAD",
        8: "PUSH_UPDATE",
    }

    _NAMES_TO_VALUES = {
        "PING": 1,
        "REGISTER": 2,
        "EXIST_MODEL": 3,
        "CAN_PULL": 4,
        "CAN_PUSH": 5,
        "PULL_MODEL": 6,
        "PUSH_GRAD": 7,
        "PUSH_UPDATE": 8,
    }


class Grad(object):
    """
    Attributes:
     - id
     - learning_rate
     - length
     - data
     - n_iter
     - worker_id

    """


    def __init__(self, id=None, learning_rate=None, length=None, data=None, n_iter=None, worker_id=None,):
        self.id = id
        self.learning_rate = learning_rate
        self.length = length
        self.data = data
        self.n_iter = n_iter
        self.worker_id = worker_id

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.id = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.DOUBLE:
                    self.learning_rate = iprot.readDouble()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.length = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.LIST:
                    self.data = []
                    (_etype3, _size0) = iprot.readListBegin()
                    for _i4 in range(_size0):
                        _elem5 = iprot.readDouble()
                        self.data.append(_elem5)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.I32:
                    self.n_iter = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.I32:
                    self.worker_id = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('Grad')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.STRING, 1)
            oprot.writeString(self.id.encode('utf-8') if sys.version_info[0] == 2 else self.id)
            oprot.writeFieldEnd()
        if self.learning_rate is not None:
            oprot.writeFieldBegin('learning_rate', TType.DOUBLE, 2)
            oprot.writeDouble(self.learning_rate)
            oprot.writeFieldEnd()
        if self.length is not None:
            oprot.writeFieldBegin('length', TType.I32, 3)
            oprot.writeI32(self.length)
            oprot.writeFieldEnd()
        if self.data is not None:
            oprot.writeFieldBegin('data', TType.LIST, 4)
            oprot.writeListBegin(TType.DOUBLE, len(self.data))
            for iter6 in self.data:
                oprot.writeDouble(iter6)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.n_iter is not None:
            oprot.writeFieldBegin('n_iter', TType.I32, 5)
            oprot.writeI32(self.n_iter)
            oprot.writeFieldEnd()
        if self.worker_id is not None:
            oprot.writeFieldBegin('worker_id', TType.I32, 6)
            oprot.writeI32(self.worker_id)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class Update(object):
    """
    Attributes:
     - id
     - length
     - data
     - n_iter
     - worker_id

    """


    def __init__(self, id=None, length=None, data=None, n_iter=None, worker_id=None,):
        self.id = id
        self.length = length
        self.data = data
        self.n_iter = n_iter
        self.worker_id = worker_id

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.id = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I32:
                    self.length = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.data = []
                    (_etype10, _size7) = iprot.readListBegin()
                    for _i11 in range(_size7):
                        _elem12 = iprot.readDouble()
                        self.data.append(_elem12)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.n_iter = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.I32:
                    self.worker_id = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('Update')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.STRING, 1)
            oprot.writeString(self.id.encode('utf-8') if sys.version_info[0] == 2 else self.id)
            oprot.writeFieldEnd()
        if self.length is not None:
            oprot.writeFieldBegin('length', TType.I32, 2)
            oprot.writeI32(self.length)
            oprot.writeFieldEnd()
        if self.data is not None:
            oprot.writeFieldBegin('data', TType.LIST, 3)
            oprot.writeListBegin(TType.DOUBLE, len(self.data))
            for iter13 in self.data:
                oprot.writeDouble(iter13)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.n_iter is not None:
            oprot.writeFieldBegin('n_iter', TType.I32, 4)
            oprot.writeI32(self.n_iter)
            oprot.writeFieldEnd()
        if self.worker_id is not None:
            oprot.writeFieldBegin('worker_id', TType.I32, 5)
            oprot.writeI32(self.worker_id)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class Model(object):
    """
    Attributes:
     - id
     - length
     - data

    """


    def __init__(self, id=None, length=None, data=None,):
        self.id = id
        self.length = length
        self.data = data

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.id = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I32:
                    self.length = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.data = []
                    (_etype17, _size14) = iprot.readListBegin()
                    for _i18 in range(_size14):
                        _elem19 = iprot.readDouble()
                        self.data.append(_elem19)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('Model')
        if self.id is not None:
            oprot.writeFieldBegin('id', TType.STRING, 1)
            oprot.writeString(self.id.encode('utf-8') if sys.version_info[0] == 2 else self.id)
            oprot.writeFieldEnd()
        if self.length is not None:
            oprot.writeFieldBegin('length', TType.I32, 2)
            oprot.writeI32(self.length)
            oprot.writeFieldEnd()
        if self.data is not None:
            oprot.writeFieldBegin('data', TType.LIST, 3)
            oprot.writeListBegin(TType.DOUBLE, len(self.data))
            for iter20 in self.data:
                oprot.writeDouble(iter20)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class InvalidOperation(TException):
    """
    Attributes:
     - whatOp
     - why

    """


    def __init__(self, whatOp=None, why=None,):
        self.whatOp = whatOp
        self.why = why

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I32:
                    self.whatOp = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.why = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('InvalidOperation')
        if self.whatOp is not None:
            oprot.writeFieldBegin('whatOp', TType.I32, 1)
            oprot.writeI32(self.whatOp)
            oprot.writeFieldEnd()
        if self.why is not None:
            oprot.writeFieldBegin('why', TType.STRING, 2)
            oprot.writeString(self.why.encode('utf-8') if sys.version_info[0] == 2 else self.why)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __str__(self):
        return repr(self)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(Grad)
Grad.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'id', 'UTF8', None, ),  # 1
    (2, TType.DOUBLE, 'learning_rate', None, None, ),  # 2
    (3, TType.I32, 'length', None, None, ),  # 3
    (4, TType.LIST, 'data', (TType.DOUBLE, None, False), None, ),  # 4
    (5, TType.I32, 'n_iter', None, None, ),  # 5
    (6, TType.I32, 'worker_id', None, None, ),  # 6
)
all_structs.append(Update)
Update.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'id', 'UTF8', None, ),  # 1
    (2, TType.I32, 'length', None, None, ),  # 2
    (3, TType.LIST, 'data', (TType.DOUBLE, None, False), None, ),  # 3
    (4, TType.I32, 'n_iter', None, None, ),  # 4
    (5, TType.I32, 'worker_id', None, None, ),  # 5
)
all_structs.append(Model)
Model.thrift_spec = (
    None,  # 0
    (1, TType.STRING, 'id', 'UTF8', None, ),  # 1
    (2, TType.I32, 'length', None, None, ),  # 2
    (3, TType.LIST, 'data', (TType.DOUBLE, None, False), None, ),  # 3
)
all_structs.append(InvalidOperation)
InvalidOperation.thrift_spec = (
    None,  # 0
    (1, TType.I32, 'whatOp', None, None, ),  # 1
    (2, TType.STRING, 'why', 'UTF8', None, ),  # 2
)
fix_spec(all_structs)
del all_structs
