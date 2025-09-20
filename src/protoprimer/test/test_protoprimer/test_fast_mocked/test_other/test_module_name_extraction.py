from local_test.base_test_class import BaseTestClass
from protoprimer import primer_kernel


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_module_name_extraction(self):
        self.assertEqual(
            primer_kernel.__name__,
            "protoprimer.primer_kernel",
        )
