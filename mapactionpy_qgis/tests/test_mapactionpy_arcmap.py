import mapactionpy_arcmap.arcmap_runner as arcmap_runner
import os
import six
import sys
from itertools import repeat
# from unittest import TestCase
from unittest import TestCase, skip
from datetime import datetime
import pytz

# import unittest
import fixtures

from mapactionpy_controller.crash_move_folder import CrashMoveFolder
from mapactionpy_controller.event import Event
from mapactionpy_controller.map_recipe import MapRecipe
from mapactionpy_controller.layer_properties import LayerProperties
import mapactionpy_controller.xml_exporter as xml_exporter

# works differently for python 2.7 and python 3.x
if six.PY2:
    import mock  # noqa: F401
else:
    from unittest import mock  # noqa: F401


class TestArcMapRunner(TestCase):

    def setUp(self):
        self.parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.path_to_valid_cmf_des = os.path.join(
            self.parent_dir, 'tests', 'test_data', 'fixture_cmf_description_flat_test.json')
        self.cmf = CrashMoveFolder(self.path_to_valid_cmf_des)
        self.event = Event(os.path.join(self.cmf.path, 'event_description.json'))
        self.arcmap_runner = arcmap_runner.ArcMapRunner(self.event)

        # 1) insert map
        self.df1 = mock.Mock(name='data_frame1')
        self.df1.name = 'data_frame1'
        self.df1.elementHeight = 19
        self.df1.elementWidth = 17
        # 2) main map
        self.df2 = mock.Mock(name='data_frame2')
        self.df2.name = 'data_frame2'
        self.df2.elementHeight = 100
        self.df2.elementWidth = 200
        # 3) main map (same size different asspect ratio)
        self.df3 = mock.Mock(name='data_frame3')
        self.df3.name = 'data_frame3'
        self.df3.elementHeight = 50
        self.df3.elementWidth = 400
        # 4) main map - identical to df3
        self.df4 = mock.Mock(name='data_frame4')
        self.df4.name = 'data_frame4'
        self.df4.elementHeight = 50
        self.df4.elementWidth = 400
        # 5) main map - widest, but not the largest area
        self.df5 = mock.Mock(name='data_frame5')
        self.df5.name = 'data_frame5'
        self.df5.elementHeight = 10
        self.df5.elementWidth = 500
        # 6) inset map - identical to df1 in every way including the name
        self.df6 = mock.Mock(name='data_frame6')
        self.df6.name = 'data_frame1'
        self.df6.elementHeight = 19
        self.df6.elementWidth = 17

    @mock.patch('mapactionpy_arcmap.arcmap_runner.arcpy.mapping.MapDocument')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.arcpy.mapping.ListDataFrames')
    def test_get_aspect_ratios_of_templates(self, mock_ListDataFrames, mock_MapDocument):
        mock_MapDocument.return_value = None
        df_lists = [
            [self.df1], [self.df2], [self.df3], [self.df4], [self.df5], [self.df6]
        ]
        mock_ListDataFrames.side_effect = df_lists
        tmpl_paths = repeat('/the/path', len(df_lists))
        tmpl_paths = ['/the/path{}'.format(n) for n in range(1, 7)]

        test_lp = LayerProperties(self.cmf, '.lyr')
        test_recipe = MapRecipe(fixtures.fixture_recipe_minimal, test_lp)

        expected_result = [
            ('/the/path1', float(self.df1.elementWidth)/self.df1.elementHeight),
            ('/the/path2', float(self.df2.elementWidth)/self.df2.elementHeight),
            ('/the/path3', float(self.df3.elementWidth)/self.df3.elementHeight),
            ('/the/path4', float(self.df4.elementWidth)/self.df4.elementHeight),
            ('/the/path5', float(self.df5.elementWidth)/self.df5.elementHeight),
            ('/the/path6', float(self.df6.elementWidth)/self.df6.elementHeight)
        ]

        actual_result = self.arcmap_runner.get_aspect_ratios_of_templates(tmpl_paths, test_recipe)

        self.assertEqual(actual_result, expected_result)

    @mock.patch('mapactionpy_arcmap.arcmap_runner.arcpy.mapping.ExportToJPEG')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.arcpy.mapping.ExportToPDF')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.ArcMapRunner.export_png_thumbnail')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.arcpy.mapping.MapDocument')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.os.path.getsize')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.get_map_scale')
    @mock.patch('mapactionpy_arcmap.arcmap_runner.get_map_spatial_ref')
    def test_do_export_params(self, mock_jpeg, mock_pdf, mock_png, mock_mapdoc, mock_getsize,
                              mock_scale, mock_spatial_ref):
        mock_jpeg.return_value = '/abc/xyz.jpeg'
        mock_pdf.return_value = '/abc/xyz.pdf'
        mock_png.return_value = '/abc/xyz.png'
        mock_mapdoc.return_value = None
        mock_getsize.return_value = 9999
        mock_scale.return_value = '1:123456 at A3'
        mock_spatial_ref.return_value = 'WGS 1984'

        test_lp = LayerProperties(self.cmf, '.lyr')
        test_recipe = MapRecipe(fixtures.fixture_recipe_minimal, test_lp)
        test_recipe.export_path = self.cmf.path
        test_recipe.creation_time_stamp = datetime.now(pytz.utc)
        test_recipe.map_project_path = os.path.join(
            self.parent_dir, 'tests', 'test_data', 'arcgis_10_6_reference_landscape_bottom.mxd')

        initial_export_params = {}
        initial_export_params["exportDirectory"] = os.path.join(
            self.parent_dir, 'tests', 'test_data', 'outputs')

        self.arcmap_runner._do_export(test_recipe)
        # This will fail with a ValueError if the right metadata data isn't available
        xml_exporter._check_for_export_metadata(test_recipe)
        # self.fail()

    @skip('Not ready yet')
    def test_arcmap_runner_main(self):
        sys.argv[1:] = ['--eventConfigFile', os.path.join(self.cmf.path, 'event_description.json'),
                        '--template', os.path.join(self.cmf.map_templates,
                                                   'arcgis_10_6_reference_landscape_bottom.mxd'),
                        "--product", "Example Map"]

        arcmap_runner.main()
        self.assertTrue(True)

    @skip('Not ready yet')
    def test_arcmap_runner_main_unknown_product(self):
        sys.argv[1:] = ['--eventConfigFile', os.path.join(self.cmf.path, 'event_description.json'),
                        '--template', os.path.join(self.cmf.map_templates,
                                                   'arcgis_10_6_reference_landscape_bottom.mxd'),
                        "--product", "This product does not exist"]
        try:
            arcmap_runner.main()
        except Exception as e:
            self.assertTrue("Could not find recipe for product: \"" +
                            sys.argv[6] + "\"" in str(e.message))
