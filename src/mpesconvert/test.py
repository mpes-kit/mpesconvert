from FileConverter import Convertor
fc = Convertor(definition='ARPES', data_dir= './tutorial/data.h5', metadata_dir='./tutorial/metadata.yaml')
fc.to_nexus('./tutorial/test_file', 'V', 'kx', 'ky', 'E', 'delay')