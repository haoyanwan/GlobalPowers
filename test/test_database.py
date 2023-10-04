import unittest
import pymongo


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = pymongo.MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client["your_database_name"]
        cls.collection = cls.db["tournaments"]

    def test_missing_values(self):
        # Fields you want to check for missing values
        fields_to_check = ["id", "name", "image", "region"]

        # Query for documents where any of the fields are missing
        missing_values = list(self.collection.find({"$or": [{field: {"$exists": False}} for field in fields_to_check]}))

        # If any documents are returned by the query, the test will fail
        self.assertFalse(missing_values, f"Documents with missing values: {missing_values}")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()


if __name__ == "__main__":
    unittest.main()