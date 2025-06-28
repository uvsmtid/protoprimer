from protoprimer import primer_kernel
from test_support import BaseTestClass


# noinspection PyMethodMayBeStatic
class ThisTestClass(BaseTestClass):

    def test_module_name_extraction(self):
        self.assertEqual(
            primer_kernel.__name__,
            "protoprimer.primer_kernel",
        )
