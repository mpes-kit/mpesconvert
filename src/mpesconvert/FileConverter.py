import h5py
import numpy as np
import os
import yaml
from nexusformat.nexus import *

"""
    author:: Muhammad Zain Sohail
"""
class Convertor():
    def __init__(self, type_=None, metadata_dir='metadata.yaml', data_dir='data.h5'):
        root = self.createNXmpes(type_)
        self.data = h5py.File(data_dir, 'r')
        
        self.data_group='data'
        if type_:
            self.data_group = 'process'
            
        with open(metadata_dir) as f:
            metadata_all = yaml.load_all(f, Loader=yaml.FullLoader)
            for doc in metadata_all:
                for key, value in doc.items():
                    if key =='general':
                        NX_group = self.YAMLMetadataParser(value, root.entry)
                    else:
                        NX_group[key] = self.YAMLMetadataParser(value, root.entry[key])
        self.NX = NX_group                
                        
    def to_nexus(self, nx_filename, signal, *axes):
        self.createNXData(self.NX[self.data_group], signal, *axes)
        self.NX.save(nx_filename + '.nxs', mode='w')
        print(self.NX.tree)
    
    def createNXmpes(self, type_):
        root=NXroot(NXentry())
        root.entry.definition=NXfield('NXmpes') 
        root.entry.instrument=NXinstrument()
        root.entry.instrument.beam_probe_0=NXbeam()
        root.entry.instrument.manipulator=NXpositioner()
        root.entry.instrument.analyser=NXdetector()
        root.entry.sample=NXsample()

        if type_ == 'ARPES':
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

    def createNXData(self, subgroup, signal, *axes):
        all_axes = []
        for axis in axes:
            all_axes.append(subgroup[axis])
        self.NX.data=NXdata(subgroup[signal], [*all_axes])

    def YAMLMetadataParser(self, group, NX_group):
        main_group = group
        NX_group_copy = NX_group
        for key, item in group.items():
            subgroup = group
            if isinstance(subgroup, dict):
                subgroup = subgroup[key]
                if not isinstance(subgroup, dict):
                    NX_group_copy[key] = NXfield(subgroup)
                    NX_group = NX_group_copy
                if 'value' in subgroup:
                    value = subgroup['value']
                    if ('unit' in subgroup) & ('name' not in subgroup):
                        unit = subgroup['unit']
                        NX_group_copy[key] = NXfield(value, units=unit)
                        NX_group = NX_group_copy
                    elif ('unit' in subgroup) & ('name'in subgroup):
                        unit = subgroup['unit']
                        name = subgroup['name'] 
                        NX_group_copy[key] = NXfield(self.data[value], name=name, units=unit)
                        NX_group = NX_group_copy
                    else:
                        NX_group_copy[key] = NXfield(value)
                        NX_group = NX_group_copy
                elif isinstance(subgroup, dict) & ('value' not in subgroup):
                    NX_subgroup = self.YAMLMetadataParser(subgroup, NX_group[key])
                    NX_group_copy[key] = NX_subgroup
                    NX_group = NX_group_copy
        return NX_group
