import os
import unittest
import pipeline
import pandas as pd
import numpy as np


class BaseTest(unittest.TestCase):
    def setUp(self):
        self._address_list_fname = 'test_address_list.csv'
        self._postcode_reference_fname = 'test_postcode_reference.csv'
        self._destination_fname = 'test_address_list.tsv'

        if os.path.isfile(self._destination_fname):
            os.remove(self._destination_fname)

    def _import_results_for_analysis(self):
        if not os.path.isfile(self._destination_fname):
            pipeline.run(self._address_list_fname, self._postcode_reference_fname, self._destination_fname)
        return pd.read_csv(self._destination_fname, sep='\t')

    def _template_test(self, pos, urn, postcode, validated):
        df = self._import_results_for_analysis()
        record = df.iloc[pos, :]

        self.assertEqual(record['urn'], urn)
        if pd.isna(postcode):
            self.assertTrue(pd.isna(record['Postcode']))
        else:
            self.assertEqual(record['Postcode'], postcode)
        self.assertEqual(record['validated'], validated)


class TestPipeline(BaseTest):
    def test_pipeline(self):
        pipeline.run(self._address_list_fname, self._postcode_reference_fname, self._destination_fname)

        # Check that the file has been created
        self.assertTrue(os.path.isfile(self._destination_fname))

        # Check that it is a tsv that can be imported
        df = pd.read_csv(self._destination_fname, sep='\t')

        self.assertTrue(isinstance(df, pd.DataFrame))

        # Check the columns are what we expect
        expected_columns = ["urn", "Registration Date", "Latitude", "Longitude",
                            "Location", "Unnamed: 5", "Postcode", "validated"]

        self.assertTrue(all(df.columns == expected_columns))

        # Check we have the same rows
        self.assertEqual(df.shape[0], 6)

    def test_valid_current_match(self):
        self._template_test(pos=0, urn=1, postcode='IG8 0NS', validated=True)

    def test_no_postcode(self):
        self._template_test(pos=1, urn=2, postcode=np.nan, validated=False)

    def test_not_within_date_range(self):
        self._template_test(pos=2, urn=3, postcode=np.nan, validated=False)

    def test_too_distant(self):
        self._template_test(pos=3, urn=4, postcode=np.nan, validated=False)

    def test_invalid_coordinate(self):
        self._template_test(pos=4, urn=5, postcode=np.nan, validated=False)

    def test_valid_historic_match(self):
        self._template_test(pos=5, urn=6, postcode='IG4 1PU', validated=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
