from django.test import (
    TestCase as BaseTestCase,
    TransactionTestCase as BaseTransactionTestCase,
)


class TestServerSiteMixin:
    def setUp(self):
        from django.contrib.sites.models import Site

        self.site = Site.objects.first()
        self.site.domain = "testserver"
        self.site.name = "testserver"
        self.site.save()


class TestCase(TestServerSiteMixin, BaseTestCase):
    pass


class TransactionTestCase(TestServerSiteMixin, BaseTransactionTestCase):
    pass
