"""

 Summary:
    Contains the BridgeUnit, BridgeUspbrUnit and BridgeArchUnit classed.
    The BridgeUnit is a superclass to the other containing default shared
    behaviour and content.
    These hold all of the data read in from the bridge units in the dat file.
    Can be called to load in the data and read and update the contents 
    held in the object.

 Author:  
     Duncan Runnacles

  Created:  
     01 Apr 2016

 Copyright:  
     Duncan Runnacles 2016

 TODO:

 Updates:

"""
import math

from ship.isis.datunits.isisunit import AIsisUnit
from ship.data_structures.dataobject import DataTypes
from ship.data_structures.rowdatacollection import RowDataCollection
from ship.isis.datunits import ROW_DATA_TYPES as rdt
from ship.utils.tools import geometry

from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)
"""logging references with a __name__ set to this module."""


class BridgeUnit (AIsisUnit): 
    """Subclass of AIsisUnit storing Isis Bridge Unit data.

    Note:
        This really an abstract class for any bridge unit and is not really
        intended to be used directly.

    Contains a reference to a rowdatacollection for storing and
    accessing all the row data. i.e. the geometry data for the section,
    containing the chainage, elevation, roughness, etc values.
    Methods for accessing the data in these objects and adding removing rows
    are available.
    """
    
    UNIT_TYPE = 'Bridge'
    CATEGORY = 'Bridge'
    
    UNIT_VARS = None


    def __init__(self, file_order): 
        """Constructor.
        
        Args:
            fileOrder (int): The location of this unit in the file.
        """
        AIsisUnit.__init__(self, file_order)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels.
        self.head_data = {'upstream': '', 'downstream': '', 'remote_us': '',
                          'remote_ds': '', 'roughness_type': 'MANNING',
                          'calibration_coef': 1, 'skew_angle': 1, 'width': 0,
                          'dual_distance': 0, 'no_of_orifices': 0, 
                          'orifice_flag': '', 'op_lower': 0, 'op_upper': 0, 
                          'op_cd': 0, 'comment': '', 'rowcount': 0, 
                          'row_count_additional': {'Opening': 1}} 

        self.unit_type = BridgeUnit.UNIT_TYPE
        self.unit_category = BridgeUnit.CATEGORY
        self.has_datarows = True
        self.no_of_collections = 2
        self.unit_length = 0
        self.no_of_chainage_rows = 1
        self.no_of_opening_rows = 1
        self.no_of_culvert_rows = 0
        self.additional_row_collections = OrderedDict()
        
        
    def getNumberOfOpenings(self):
        """
        """
        return self.no_of_opening_rows
    
    
    def getArea(self):
        """Returns the cross sectional area of the bridge openings.    
        
        Return:
            Dict - containing the area of the opening(s). keys = 'total', then
                '1', '2', 'n' for all openings found.
        """
        return 0
#         areas = []
#         opening_data = self.additional_row_collections['Opening']
#         x_vals = self.row_collection.getRowDataAsList(rdt.CHAINAGE)
#         y_vals = self.row_collection.getRowDataAsList(rdt.ELEVATION)
#         
#         start_vals = opening_data.getRowDataAsList(rdt.OPEN_START)
#         end_vals = opening_data.getRowDataAsList(rdt.OPEN_END)
#         soffit_vals = opening_data.getRowDataAsList(rdt.SOFFIT_LEVEL)
#         springing_vals = opening_data.getRowDataAsList(rdt.SPRINGING_LEVEL)
#         openings = zip(start_vals, end_vals, soffit_vals, springing_vals)
#         
#         for i, x in enumerate(x_vals):
#             
#             if math.fabs(x - ) 
#         
#         
#         i=0

    def readUnitData(self, unit_data, file_line):
        """Reads the unit data into the geometry objects.
        
        See Also:
            AIsisUnit
            
        Args: 
            unit_data (list): The section of the isis dat file pertaining to 
                this section. 
        """
        file_line = self._readHeadData(unit_data, file_line)
        self.name = self.head_data['upstream']
        file_line = self._readMainRowData(unit_data, file_line)
        file_line = self._readAdditionalRowData(unit_data, file_line)
        self.head_data['rowcount'] = self.row_collection.getNumberOfRows()
        
        for key, data in self.additional_row_collections.iteritems():
            self.head_data['row_count_additional'][key] = data.getNumberOfRows()
        
        return file_line
        

    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        Note:
            Must be implemented by subclass
            
        Raises:
            NotImplementedError: if not overriden by sub class.
        """
        raise NotImplementedError


    def _readMainRowData(self, unit_data, file_line):
        """Reads the units rows into the row collection.

        This is all the geometry data that occurs after the no of rows variable in
        the Bridge Units of the dat file.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        """ 
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.row_collection = RowDataCollection()
        self.row_collection.initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CHAINAGE, '{:>10}', None, 0, 3])
        self.row_collection.initCollection(DataTypes.FLOAT_DATA, vars = [rdt.ELEVATION, '{:>10}', None, 1, 3])
        self.row_collection.initCollection(DataTypes.FLOAT_DATA, vars = [rdt.ROUGHNESS, '{:>10}', 0.0, 2, 3]) 
        self.row_collection.initCollection(DataTypes.CONSTANT_DATA, vars = [rdt.EMBANKMENT, '{:>11}', '', 3, ('L', 'R')])
        
        self.unit_length = 6 #self.UNIT_VARS['Vars']['headlength']
        out_line = file_line + self.no_of_chainage_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the river section.
                self.row_collection.addValue(rdt.CHAINAGE, unit_data[i][0:10].strip())
                self.row_collection.addValue(rdt.ELEVATION, unit_data[i][10:20].strip())
                self.row_collection.addValue(rdt.ROUGHNESS, unit_data[i][20:30].strip())
                # Might not exist
                try:
                    bank = unit_data[i][40:51].strip()
                except:
                    bank = ''
                self.row_collection.addValue(rdt.EMBANKMENT, bank)
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
#         except IndexError:
#             logger.error('Unable to read Unit Data - Attempt to access index out of range')
#             raise ('Unable to read Unit Data - Attempt to access index out of range')

#         self.no_of_opening_rows = int(unit_data[self.UNIT_VARS['Vars']['headlength']+self.no_of_chainage_rows])
        self.no_of_opening_rows = int(unit_data[out_line].strip())
        self.unit_length += self.no_of_chainage_rows + 1
        return out_line + 1
    

    def getData(self): 
        """Retrieve the data in this unit.

        See Also:
            AIsisUnit - getData()
            
        Returns:
            String list - output data formated the same as in the .DAT file.
        """
        out_data = self._getHeadData()
        out_data.extend(self._getRowData()) 
        out_data.extend(self._getAdditionalRowData())
        
        return out_data
    
    
    def _formatDataItem(self, item, col_width, no_of_dps=None,
                                    is_head_item=True, align_right=True):
        """Format the given head data item for printing to file.
        """
        if is_head_item:
            item = self.head_data[item]
        if not no_of_dps == None:
            form = '%0.' + str(no_of_dps) + 'f'
            item = form % float(item)
        
        if align_right:
            final_str = '{:>' + str(col_width) + '}'
        else:
            final_str = '{:<' + str(col_width) + '}'
        return final_str.format(item)
  
  
    def _getRowData(self):
        """For all the rows in the river geometry section get the data from
        the rowdatacollection class.

        Returns:
            list - containing the formatted unit rows.
        """
        out_data = []
        no_of_rows = self.row_collection.getNumberOfRows()
        out_data.append(self._formatDataItem(no_of_rows, 10, is_head_item=False))
        for i in range(0, no_of_rows): 
            out_data.append(self.row_collection.getPrintableRow(i))
        
        return out_data
    
    
    def _getAdditionalRowData(self):
        """Get the formatted row data for any additional row data objects.
        
        Returns:
            list - containing additional row data.
        """
        out_data = []
        for data in self.additional_row_collections.itervalues():
            no_of_rows = data.getNumberOfRows()
            out_data.append(self._formatDataItem(no_of_rows, 10,
                                                 is_head_item=False))
            for i in range(0, no_of_rows):
                out_data.append(data.getPrintableRow(i))
        
        return out_data
   
  
    def _getHeadData(self):
        """Get the header data formatted for printing out
        
        Note:
            Must be implemented by concrete subclass.
        
        Raises:
            NotImplementedError: if not overridden by sub class
        """
        raise NotImplementedError
    
   
    def updateDataRow(self, row_vals, index, collection_name=None):
        """Updates the row at the given index in the river units row_collection.
        
        The row will be updated at the given index. 

        Args:
            row_vals(Dict): keys must be datunits.ROW_DATA_TYPES with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index: the row to update. 
            collection_name=None(str): If None the self.row_collection
                with the bridges geometry data will be updated. If a string it
                will be looked for in the self.additional_row_collections
                dictionary or raise an AttributeError if it doesn't exist.

        Raises:
            KeyError: If collection_name key does not exist.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not collection_name is None:
            if not collection_name in self.additional_row_collections.keys():
                raise KeyError ('collection_name %s does not exist in row collection' % (collection_name))
        
        # Call superclass method to add the new row
#         try:
        AIsisUnit.updateDataRow(self, index=index, row_vals=row_vals)
            
#         except ValueError:
#             raise  
#         except IndexError:
#             raise 
    
   
    def addDataRow(self, row_vals, index=None, collection_name=None): 
        """Adds a new row to one of this bridge units row_collection's.
        
        The new row will be added at the given index. If no index is given it
        will be appended to the end of the collection.
        
        If no chainage or elevation values are given an AttributeError will be 
        raised as they cannot have default values. All other values can be
        ommitted. If they are they will be given defaults.
        
        Examples:
            >>> import ship.isis.datunits.rdt as rdt
            >>> unit.addDataRow({rdt.CHAINAGE:5.0, rdt.ELEVATION:36.2}, index=4)

        Args:
            row_vals(Dict): keys must be datunits.rdt with a legal
                value assigned for the DataType. Chainage and Elevation MUST
                be included.
            index=None(int): the row to insert into. The existing row at the
                given index will be moved up by one.
            collection_name=None(str): If None the self.row_collection
                with the bridges geometry data will be updated. If a string it
                will be looked for in the self.additional_row_collections
                dictionary or raise an AttributeError if it doesn't exist.

        Raises:
            AttributeError: If CHAINAGE or ELEVATION are not given.
            KeyError: if the collection_name does not exist.
            IndexError: If the index does not exist.
            ValueError: If the given value is not accepted by the DataObject's. 
            
        See Also:
            ADataObject and subclasses for information on the parameters.
        """
        if not rdt.CHAINAGE in row_vals.keys() or not rdt.ELEVATION in row_vals.keys():
            logger.error('Required values of CHAINAGE and ELEVATION not given')
            raise  AttributeError ('Required values of CHAINAGE and ELEVATION not given')
        
        if not collection_name is None:
            if not collection_name in self.additional_row_collections.keys():
                raise KeyError ('collection_name %s does not exist in row collection' % (collection_name))
        
        # Setup default values for arguments that aren't given
        kw={}
        kw[rdt.CHAINAGE] = row_vals.get(rdt.CHAINAGE)
        kw[rdt.ELEVATION] = row_vals.get(rdt.ELEVATION)
        kw[rdt.ROUGHNESS] = row_vals.get(rdt.ROUGHNESS, 0.039)
        kw[rdt.PANEL_MARKER] = row_vals.get(rdt.PANEL_MARKER, False)
        kw[rdt.RPL] = row_vals.get(rdt.RPL, 1.0)
        kw[rdt.BANKMARKER] = row_vals.get(rdt.BANKMARKER, '')
        kw[rdt.EASTING] = row_vals.get(rdt.EASTING, 0.0)
        kw[rdt.NORTHING] = row_vals.get(rdt.NORTHING, 0.0)
        kw[rdt.DEACTIVATION] = row_vals.get(rdt.DEACTIVATION, '')
        kw[rdt.SPECIAL] = row_vals.get(rdt.SPECIAL, '')

        # Call superclass method to add the new row
#         try:
        AIsisUnit.addDataRow(self, index=index, row_vals=kw, 
                                            collection_name=collection_name)
            
#         except ValueError:
#             raise  
#         except IndexError:
#             raise 
    
    
    def _checkChainageIncreaseNotNegative(self, index, chainageValue):
        """Checks that new chainage value is not not higher than the next one.

        If the given chainage value for the given index is higher than the
        value in the following row ISIS will give a negative chainage error.

        It will return true if the value is the last in the row.
        
        Args:
            index (int): The index that the value is to be added at.
            chainageValue (float): The chainage value to be added.
        
        Returns:
           False if greater or True if less.
        """
        if index == None:
            return True
        
        if not index == 0:
            if self.row_collection.getDataValue(rdt.CHAINAGE, index - 1) >= chainageValue:
                return False
        
        if self.row_collection.getDataValue(rdt.CHAINAGE, index) <= chainageValue:
            return False
            
        return True
        


class BridgeUnitUsbpr (BridgeUnit): 
    """Concrete implementation of BridgeUnit for USBPR type bridges.
    
    Contains methods that override superclass with USBPR specific variables
    and file read/write behaviour.
    """
    
    UNIT_TYPE = 'Usbpr'
    CATEGORY = 'Bridge'
    FILE_KEY = 'BRIDGE'

    UNIT_VARS = {'File_id': 'USBPR1978', 
                 'Vars': {'headlength': 9, 
                          'rowlengthpos': 8, 
                          'index_shift': -1,
                          'additional_row_data': 2,
                          'Subfile_id': 'USBPR1978'
                          }
                } 

    def __init__(self, file_order): 
        """Constructor.
        
        See Also:
            BridgeUnit
        """
        BridgeUnit.__init__(self, file_order)

        # Fill in the header values these contain the data at the top of the
        # section, such as the unit name and labels. #dict(self.head_data, **
        self.head_data = dict(self.head_data, **{'pier_width': 0, 'abutment_type': 1, 
                          'no_of_piers': 0, 'pier_shape': '', 'pier_faces': '', 
                          'pier_calibration_coeff': 0, 'abutment_align': '', 
                          'no_arches': 0, 'no_culverts': 0})
        self.head_data['row_count_additional'] = {'Opening': 1, 'Orifice': 0}

        self.unit_type = 'Usbpr'
        self.unit_category = BridgeUnit.CATEGORY
        self.has_datarows = True
        self.no_of_collections = 3
        self.additional_row_collections['Opening'] = None
        self.additional_row_collections['Orifice'] = None
        
    
    def _getHeadData(self):
        """Return the extracted header data.
        
        See Also:
            BridgeUnit
        """
        out_data = []
        out_data.append('BRIDGE ' + self.head_data['comment'])
        out_data.append('USBPR1978')
        out_data.append(self._formatDataItem('upstream', 12, align_right=False) + 
                        self._formatDataItem('downstream', 12, align_right=False) +
                        self._formatDataItem('remote_us', 12, align_right=False) +
                        self._formatDataItem('remote_ds', 12, align_right=False)
                        )
        out_data.append('MANNING')
        out_data.append(self._formatDataItem('calibration_coef', 10, 3) +
                        self._formatDataItem('skew_angle', 10, 3) +
                        self._formatDataItem('width', 10, 3) +
                        self._formatDataItem('dual_distance', 10, 3) +
                        self._formatDataItem('no_of_orifices', 10) +
                        self._formatDataItem('orifice_flag', 10) +
                        self._formatDataItem('op_lower', 10, 3) +
                        self._formatDataItem('op_upper', 10, 3) +
                        self._formatDataItem('op_cd', 10, 3)
                        )
        out_data.append(self._formatDataItem('abutment_type', 10))
        out_data.append(self._formatDataItem('no_of_piers', 10) +
                        self._formatDataItem('pier_shape', 10, align_right=False) +
                        self._formatDataItem('pier_shape_2', 10) +
                        self._formatDataItem('pier_calibration_coeff', 10)
                        )
        out_data.append(self._formatDataItem('abutment_align', 10))
        
        return out_data 
    
    
    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        See Also:
            BridgeUnit
        """
        self.head_data['comment'] = unit_data[file_line][6:].strip()
        self.name = self.head_data['upstream'] = unit_data[file_line + 2][:12].strip()
        self.head_data['downstream'] = unit_data[file_line + 2][12:24].strip()
        self.head_data['remote_us'] = unit_data[file_line + 2][24:36].strip()
        self.head_data['remote_ds'] = unit_data[file_line + 2][36:48].strip()
        self.head_data['calibration_coef'] = unit_data[file_line + 4][:10].strip()
        self.head_data['skew_angle'] = unit_data[file_line + 4][10:20].strip()
        self.head_data['width'] = unit_data[file_line + 4][20:30].strip()
        self.head_data['dual_distance'] = unit_data[file_line + 4][30:40].strip()
        self.head_data['no_of_orifices'] = unit_data[file_line + 4][40:50].strip()
        self.head_data['orifice_flag'] = unit_data[file_line + 4][50:60].strip()
        self.head_data['op_lower'] = unit_data[file_line + 4][60:70].strip()
        self.head_data['op_upper'] = unit_data[file_line + 4][70:80].strip()
        self.head_data['op_cd'] = unit_data[file_line + 4][80:90].strip()
        self.head_data['abutment_type'] = unit_data[file_line + 5][0:10].strip()
        self.head_data['no_of_piers'] = unit_data[file_line + 6][:10].strip()
        self.head_data['pier_shape'] = unit_data[file_line + 6][10:20].strip()
        self.head_data['pier_shape_2'] = unit_data[file_line + 6][20:30].strip()
        self.head_data['pier_calibration_coeff'] = unit_data[file_line + 6][30:40].strip()
        self.head_data['abutment_align'] = unit_data[file_line + 7][:10].strip()
       
        self.no_of_chainage_rows = int(unit_data[file_line + 8].strip())
        return file_line + 9


    def _readAdditionalRowData(self, unit_data, file_line):
        """Get any additional data rows.
        
        See Also:
            BridgeUnit
        """
        file_line = self._readArchRowData(unit_data, file_line)
        file_line = self._readOrificeRowData(unit_data, file_line)
        return file_line
    

    def _readArchRowData(self, unit_data, file_line):
        """Load the data defining the openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
            
        TODO:
            Change the name of this function to _readOpeningRowData.
        """ 
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.additional_row_collections['Opening'] = RowDataCollection()
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.OPEN_START, '{:>10}', None, 0, 3])
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.OPEN_END, '{:>10}', None, 1, 3])
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.SPRINGING_LEVEL, '{:>10}', 0.0, 2, 3]) 
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.SOFFIT_LEVEL, '{:>10}', 0.0, 3, 3]) 
        
        out_line = file_line + self.no_of_opening_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the river section.
                self.additional_row_collections['Opening'].addValue(rdt.OPEN_START, unit_data[i][0:10].strip())
                self.additional_row_collections['Opening'].addValue(rdt.OPEN_END, unit_data[i][10:20].strip())
                self.additional_row_collections['Opening'].addValue(rdt.SPRINGING_LEVEL, unit_data[i][20:30].strip())
                self.additional_row_collections['Opening'].addValue(rdt.SOFFIT_LEVEL, unit_data[i][30:40].strip())
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
#         except IndexError:
#             logger.error('Unable to read Unit Data - Attempt to access index out of range')
#             raise
        
        self.no_of_culvert_rows = int(unit_data[out_line].strip())
        self.unit_length += self.no_of_culvert_rows + 1
        return out_line
        
    
    def _readOrificeRowData(self, unit_data, file_line):
        """Load the data defining the orifice openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
        
        TODO:
            These errors are cryptic here as they're very specific to the
            RowDataCollections being accessed. Perhaps these should be made a
            little more relevant by raising a different error. Or they could
            be dealt with better here.
        """ 
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.additional_row_collections['Orifice'] = RowDataCollection()
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_INVERT, '{:>10}', None, 0, 3])
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_SOFFIT, '{:>10}', None, 1, 3])
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_AREA, '{:>10}', 0.0, 2, 3]) 
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_CD_PART, '{:>10}', 0.0, 3, 3]) 
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_CD_FULL, '{:>10}', 0.0, 4, 3]) 
        self.additional_row_collections['Orifice'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.CULVERT_DROWNING, '{:>10}', 0.0, 5, 3]) 

        out_line = file_line + self.no_of_culvert_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the river section.
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_INVERT, unit_data[i][0:10].strip())
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_SOFFIT, unit_data[i][10:20].strip())
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_AREA, unit_data[i][20:30].strip())
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_CD_PART, unit_data[i][30:40].strip())
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_CD_FULL, unit_data[i][40:50].strip())
                self.additional_row_collections['Opening'].addValue(rdt.CULVERT_DROWNING, unit_data[i][50:60].strip())
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
#         except IndexError:
#             logger.error('Unable to read Unit Data - Attempt to access index out of range')
#             raise
        
        self.unit_length += self.no_of_culvert_rows
        return out_line

        

class BridgeUnitArch (BridgeUnit): 
    """Concrete implementation of BridgeUnit for USBPR type bridges.
    
    Contains methods that override superclass with USBPR specific variables
    and file read/write behaviour.
    """
    
    # Additional values to add to the constants list
    UNIT_TYPE = 'Arch'
    CATEGORY = 'Bridge'
    FILE_KEY = 'BRIDGE'

    UNIT_VARS = {'File_id': 'ARCH', 
                 'Vars': {'headlength': 6, 
                          'rowlengthpos': 5, 
                          'index_shift': -1,
                          'additional_row_data': 1,
                          'Subfile_id': 'ARCH'
                          }
                } 

    def __init__(self, file_order): 
        """Constructor.
        
        See Also:
            BridgeUnit
        """
        BridgeUnit.__init__(self, file_order)

        self.head_data['row_count_additional'] = {'Opening': 1}

        self.unit_type = 'Arch'
        self.unit_category = BridgeUnit.CATEGORY
        self.has_datarows = True
        self.no_of_collections = 2
        self.additional_row_collections['Opening'] = None
        
    
    def _getHeadData(self):
        """Return the extracted header data.
        
        See Also:
            BridgeUnit
        """
        out_data = []
        out_data.append('BRIDGE ' + self.head_data['comment'])
        out_data.append('ARCH')
        out_data.append(self._formatDataItem('upstream', 12, align_right=False) + 
                        self._formatDataItem('downstream', 12, align_right=False) +
                        self._formatDataItem('remote_us', 12, align_right=False) +
                        self._formatDataItem('remote_ds', 12, align_right=False)
                        )
        out_data.append('MANNING')
        out_data.append(self._formatDataItem('calibration_coef', 10, 3) +
                        self._formatDataItem('skew_angle', 10, 3) +
                        self._formatDataItem('width', 10, 3) +
                        self._formatDataItem('dual_distance', 10, 3) +
                        self._formatDataItem('no_of_orifices', 10) +
                        self._formatDataItem('orifice_flag', 10) +
                        self._formatDataItem('op_lower', 10, 3) +
                        self._formatDataItem('op_upper', 10, 3) +
                        self._formatDataItem('op_cd', 10, 3)
                        )
        
        return out_data 
    
    
    def _readHeadData(self, unit_data, file_line):            
        """Format the header data for writing to file.
        
        See Also:
            BridgeUnit
        """
        self.head_data['comment'] = unit_data[file_line][6:].strip()
        self.name = self.head_data['upstream'] = unit_data[file_line + 2][:12].strip()
        self.head_data['downstream'] = unit_data[file_line + 2][12:24].strip()
        self.head_data['remote_us'] = unit_data[file_line + 2][24:36].strip()
        self.head_data['remote_ds'] = unit_data[file_line + 2][36:48].strip()
        self.head_data['calibration_coef'] = unit_data[file_line + 4][:10].strip()
        self.head_data['skew_angle'] = unit_data[file_line + 4][10:20].strip()
        self.head_data['width'] = unit_data[file_line + 4][20:30].strip()
        self.head_data['dual_distance'] = unit_data[file_line + 4][30:40].strip()
        self.head_data['no_of_orifices'] = unit_data[file_line + 4][40:50].strip()
        self.head_data['orifice_flag'] = unit_data[file_line + 4][50:60].strip()
        self.head_data['op_lower'] = unit_data[file_line + 4][60:70].strip()
        self.head_data['op_upper'] = unit_data[file_line + 4][70:80].strip()
        self.head_data['op_cd'] = unit_data[file_line + 4][80:90].strip()
       
        self.no_of_chainage_rows = int(unit_data[file_line + 5].strip())
        return file_line + 6

    def _readAdditionalRowData(self, unit_data, file_line):
        """Get any additional data rows.
        
        See Also:
            BridgeUnit
        """
        file_line = self._readArchRowData(unit_data, file_line)
        return file_line - 1
    

    def _readArchRowData(self, unit_data, file_line):
        """Load the data defining the openings in the bridge.
        
        Args:
            unit_data (list): the data pertaining to this unit.
            
        TODO:
            Change the name of this function to _readOpeningRowData.
        """ 
        # Add the new row data types to the object collection
        # All of them must have type, output format, default value and position
        # in the row as the first variables in vars.
        # The others are DataType specific.
        self.additional_row_collections['Opening'] = RowDataCollection()
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.OPEN_START, '{:>10}', None, 0, 3])
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.OPEN_END, '{:>10}', None, 1, 3])
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.SPRINGING_LEVEL, '{:>10}', 0.0, 2, 3]) 
        self.additional_row_collections['Opening'].initCollection(DataTypes.FLOAT_DATA, vars = [rdt.SOFFIT_LEVEL, '{:>10}', 0.0, 3, 3]) 
        
        out_line = file_line + self.no_of_opening_rows
        try:
            # Load the geometry data
            for i in range(file_line, out_line):
                
                # Put the values into the respective data objects            
                # This is done based on the column widths set in the Dat file
                # for the river section.
                self.additional_row_collections['Opening'].addValue(rdt.OPEN_START, unit_data[i][0:10].strip())
                self.additional_row_collections['Opening'].addValue(rdt.OPEN_END, unit_data[i][10:20].strip())
                self.additional_row_collections['Opening'].addValue(rdt.SPRINGING_LEVEL, unit_data[i][20:30].strip())
                self.additional_row_collections['Opening'].addValue(rdt.SOFFIT_LEVEL, unit_data[i][30:40].strip())
                
        except NotImplementedError:
            logger.error('Unable to read Unit Data(dataRowObject creation) - NotImplementedError')
            raise
#         except IndexError:
#             logger.error('Unable to read Unit Data - Attempt to access index out of range')
#             raise
        
        self.unit_length += self.no_of_culvert_rows + 1
        return out_line
        
 