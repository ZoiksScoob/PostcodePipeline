import os
import unittest
import pipeline
import pandas as pd


test_address_list = """urn,Registration Date,Latitude,Longitude,Location,Unnamed: 5
1,24/04/2012 00:00,51.6155,0.032659,"21, Privat Drive, IG8 0NS",
2,24/04/2012 00:00,51.5717,0.052316,"74, Canterbury Avenue, Ilford",
3,24/04/2012 00:00,51.5988,0.013589,"80, Chelmsford Road, London, E18 2PP",
4,24/04/2012 00:00,51.5958,0.074697,"236, Fullwell Avenue, Ilford, E11 1PD",
5,23/04/2012 00:00,Gibberish,0.047408,"49, Torquay Gardens, Ilford, IG4 5PU"
6,23/04/2000 00:00,51.5117,0.035408,"49, Torquay Gardens, Ilford, IG4 1PU"
"""

test_postcode_reference = """postcode,postcode_introduced,postcode_terminated,lat,long
IG8 1NS,198001,200207,51.615593,0.032658
IG8 0NS,200207,,51.615593,0.032658
E18 2PP,198001,200207,51.598833,0.013584
E11 1PD,200207,,51.598833,0.013584
IG4 5PU,198001,,51.594421,0.047404
IG4 1PU,199001,201001,51.511765,0.035402
IG3 2PU,201001,,51.511765,0.035402
"""


class BaseTest(unittest.TestCase):
    def setUp(self):
        self._address_list_fname = 'test_address_list.csv'
        self._postcode_reference_fname = 'test_postcode_reference.csv'
        self._destination_fname = 'test_result.tsv'

        with open(self._address_list_fname, 'w') as f:
            f.write(test_address_list)

        with open(self._postcode_reference_fname, 'w') as f:
            f.write(test_postcode_reference)

    def tearDown(self):
        os.remove(self._address_list_fname)
        os.remove(self._postcode_reference_fname)

    def _import_results_for_analysis(self):
        if not os.path.isfile(self._destination_fname):
            pipeline.run(self._address_list_fname, self._postcode_reference_fname, self._destination_fname)
        return pd.from_csv(self._destination_fname, sep='\t')

    def _template_test(self, pos, urn, postcode, validated):
        df = self._import_results_for_analysis()
        record = df.iloc[pos, :]

        self.assertEqual(record['urn'], urn)
        self.assertEqual(record['Postcode'], postcode)
        self.assertEqual(record['validated'], validated)



class TestPipeline(BaseTest):
    def test_pipeline(self):
        pipeline.run(self._destination_fname)

        # Check that the file has been created
        self.assertTrue(os.path.isfile(self._destination_fname))

        # Check that it is a tsv that can be imported
        df = pd.from_csv(self._destination_fname, sep='\t')

        self.assertTrue(isinstance(df, pd.DataFrame))

        # Check the columns are what we expect
        expected_columns = ["urn", "Registration Date", "Latitude", "Longitude",
                            "Location", "Unnamed: 5", "Postcode", "validated"]

        self.assertTrue(all(df.columns, expected_columns))

        # Check we have the same rows
        self.assertEqual(df.shape[0], 6)

    def test_valid_current_match(self):
        self._template_test(pos=0, urn=1, postcode='IG8 0NS', validated=True)

    def test_no_postcode(self):
        self._template_test(pos=1, urn=2, postcode=pd.nan, validated=False)

    def test_not_within_date_range(self):
        self._template_test(pos=2, urn=3, postcode=pd.nan, validated=False)

    def test_too_distant(self):
        self._template_test(pos=3, urn=4, postcode=pd.nan, validated=False)

    def test_invalid_coordinate(self):
        self._template_test(pos=4, urn=5, postcode=pd.nan, validated=False)

    def test_valid_historic_match(self):
        self._template_test(pos=5, urn=6, postcode='IG4 1PU', validated=True)


if __name__ == '__main__':
    unittest.main()
