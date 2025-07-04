from protoprimer import primer_kernel
from local_test import BaseTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_module_name_extraction(self):
        self.assertEqual(
            primer_kernel.__name__,
            "protoprimer.primer_kernel",
        )
