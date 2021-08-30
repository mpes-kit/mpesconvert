import h5py
import numpy as np
import os
import yaml
import datetime
from nexusformat.nexus import *

"""
    author:: Muhammad Zain Sohail
"""
class Convertor():
    def __init__(self, definition=None, metadata_dir='metadata.yaml', data_dir='data.h5'):
        root = self.createNXmpes(definition)
        self.data = h5py.File(data_dir, 'r')
        
        self.data_group='data'
        # if definition:
        #     self.data_group = 'process'
            
        with open(metadata_dir) as f:
            metadata_all = yaml.load_all(f, Loader=yaml.FullLoader)
            for doc in metadata_all:
                for key, value in doc.items():
                    if key =='general':
                        self.NX = self.YAMLMetadataParser(value, root.entry)
                    else:
                        self.NX[key] = self.YAMLMetadataParser(value, root.entry[key])
        self.root = root

    def createNXmpes(self, definition):
        root=NXroot(NXentry())
        root.entry.definition=NXfield('NXmpes') 
        root.entry.instrument=NXinstrument()
        root.entry.instrument.beam_probe_0=NXbeam()
        root.entry.instrument.manipulator=NXpositioner()
        root.entry.instrument.analyser=NXdetector()
        root.entry.sample=NXsample()
        root.entry.data=NXdata()

        if definition == 'ARPES':
            root.entry.definition=NXfield('ARPES')
            root.entry.user=NXuser()
            root.entry.instrument.source=NXsource()
            root.entry.instrument.source_pump=NXsource()
            root.entry.instrument.beam_pump_0=NXbeam()
            root.entry.instrument.attenuator_sn1=NXattenuator()
            root.entry.instrument.attenuator_sn2=NXattenuator()
            root.entry.instrument.attenuator_pump=NXattenuator()
            root.entry.process=NXprocess()
            root.entry.process.distortion=NXgroup(name='NXdistortion')
            root.entry.process.registration=NXgroup(name='NXregistration')
            root.entry.process.calibration_k=NXgroup(name='NXcalibration')
            root.entry.process.calibration_e=NXgroup(name='NXcalibration')
            root.entry.process.correction=NXgroup(name='NXcorrection')
            root.entry.process.enhancement=NXgroup(name='NXenhancement')
            
        return root

    def addTimeStamp(self, NX_group, key, value):
        NX_group[key + '_timestamp'] =  NXfield(value.timestamp())
        return NX_group

    def YAMLMetadataParser(self, group, NX_group):
        for key, item in group.items():
            if isinstance(group, dict):
                subgroup = group[key]
                if not isinstance(subgroup, dict):
                    NX_group[key] = NXfield(subgroup)
                if 'value' in subgroup:
                    value = subgroup['value']
                    if isinstance(value, datetime.datetime):
                        NX_group = self.addTimeStamp(NX_group, key, value)
                        value = value.strftime("%Y-%m-%dT%H:%M:%S")
                    if ('unit' in subgroup) & ('name' not in subgroup):
                        unit = subgroup['unit']
                        NX_group[key] = NXfield(value, units=unit)
                    elif ('unit' in subgroup) & ('name'in subgroup):
                        unit = subgroup['unit']
                        name = subgroup['name'] 
                        NX_group[key] = NXfield(self.data[value], name=name, units=unit)
                    else:
                        NX_group[key] = NXfield(value)
                elif isinstance(subgroup, dict) & ('value' not in subgroup):
                    NX_group[key] = self.YAMLMetadataParser(subgroup, NX_group[key])
        return NX_group
    
    def createNXData(self, subgroup, signal, *axes):
        all_axes = []
        for axis in axes:
            all_axes.append(subgroup[axis])
        self.NX.data= NXdata(subgroup[signal], all_axes)

    def to_nexus(self, nx_filename, signal, *axes):
        self.createNXData(self.NX[self.data_group], signal, *axes)
        self.root.entry = self.NX
        self.root.save(nx_filename + '.nxs', mode='w')
        print(self.NX.tree)