import luigi
from luigi.mock import MockFile
import unittest
from luigi.util import Derived

File = MockFile


class A(luigi.Task):
    def output(self):
        return File('/tmp/a.txt')

    def run(self):
        f = self.output().open('w')
        print >>f, 'hello, world'
        f.close()


class B(luigi.Task):
    date = luigi.DateParameter()

    def output(self):
        return File(self.date.strftime('/tmp/b-%Y-%m-%d.txt'))

    def run(self):
        f = self.output().open('w')
        print >>f, 'goodbye, space'
        f.close()

def XMLWrapper(cls):
    class XMLWrapperCls(Derived(cls)):
        def requires(self):
            return self.parent_obj

        def run(self):
            f = self.input().open('r')
            g = self.output().open('w')
            print >>g, '<?xml version="1.0" ?>'
            for line in f:
                print >>g, '<dummy-xml>' + line.strip() + '</dummy-xml>'
            g.close()

    return XMLWrapperCls

@luigi.expose
class AXML(XMLWrapper(A)):
    def output(self):
        return File('/tmp/a.xml')


@luigi.expose
class BXML(XMLWrapper(B)):
    def output(self):
        return File(self.date.strftime('/tmp/b-%Y-%m-%d.xml'))

class WrapperTest(unittest.TestCase):
    def test_a(self):
        luigi.run(['--local-scheduler', 'AXML'])
        self.assertEqual(MockFile._file_contents['/tmp/a.xml'], '<?xml version="1.0" ?>\n<dummy-xml>hello, world</dummy-xml>\n')

    def test_b(self):
        luigi.run(['--local-scheduler', 'BXML', '--date', '2012-01-01'])
        self.assertEqual(MockFile._file_contents['/tmp/b-2012-01-01.xml'], '<?xml version="1.0" ?>\n<dummy-xml>goodbye, space</dummy-xml>\n')


if __name__ == '__main__':
    luigi.run()
