import textwrap

from ssort._modules import Module, statement_text
from ssort._presort import presort


def _clean(source):
    return textwrap.dedent(source).strip() + "\n"


def _presort(source):
    source = _clean(source)
    module = Module(source)
    presorted = presort(module)
    return _clean(
        "\n".join(statement_text(module, stmt) for stmt in presorted)
    )


def test_isort_finders_example():
    actual = _presort(
        """
        class Base:
            pass

        def a():
            pass

        class A(Base):
            def method():
                a()

        class B(Base):
            pass

        def something():
            return [A, B]
        """
    )
    expected = _clean(
        """
        def something():
            return [A, B]

        class A(Base):
            def method():
                a()

        class B(Base):
            pass
        class Base:
            pass

        def a():
            pass
        """
    )
    assert actual == expected


def test_dnspython_versioned_example():
    actual = _presort(
        """
        import dns.exception
        import dns.transaction
        import dns.zone

        class Zone(dns.zone.Zone):

            def __init__(self):
                _threading()

            def reader(self, id=None, serial=None):
                Transaction()

            def replace_rdataset(self, name, replacement):
                raise UseTransaction

        def _threading():
            pass

        class Transaction(dns.transaction.Transaction):
            def _setup_version(self):
                WritableVersion()

        class UseTransaction(dns.exception.DNSException):
          pass

        class WritableVersion(Version):
            pass

        class Version:
            pass
        """
    )
    expected = _clean(
        """
        import dns.exception
        import dns.transaction
        import dns.zone

        class Zone(dns.zone.Zone):

            def __init__(self):
                _threading()

            def reader(self, id=None, serial=None):
                Transaction()

            def replace_rdataset(self, name, replacement):
                raise UseTransaction

        def _threading():
            pass

        class Transaction(dns.transaction.Transaction):
            def _setup_version(self):
                WritableVersion()

        class UseTransaction(dns.exception.DNSException):
          pass

        class WritableVersion(Version):
            pass

        class Version:
            pass
        """
    )
    assert actual == expected
