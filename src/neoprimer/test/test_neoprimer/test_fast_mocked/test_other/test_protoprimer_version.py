import neoprimer
from local_test.base_test_class import BaseTestClass
from local_test.package_version_verifier import verify_package_version


class ThisTestClass(BaseTestClass):

    def test_protoprimer_version(self):
        self.assertTrue(verify_package_version(neoprimer))
