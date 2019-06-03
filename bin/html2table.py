"""Parse html to table."""
from bs4 import BeautifulSoup
import os
import pandas


class Html2Table(object):
    """Find table by tag from html and output dataframe."""

    def __init__(self, htmlfile):
        """Init class."""
        if not os.path.isfile(htmlfile):
            raise ValueError("Can not find html %s!", htmlfile)
        self.htmlfile = htmlfile

    def parse(self, attributes):
        """Parse html and find table."""
        self.df_dict = {}
        with open(self.htmlfile, 'rt', encoding='utf-8') as hl:
            bsobj = BeautifulSoup(hl, 'lxml')
            for name in attributes:
                key, value = name.split(': ')
                if key == 'class':
                    key = 'class_'
                table = bsobj.find('table', **{key: value})
                df = None
                if table is not None:
                    df = self.parser_table(table, name)
                self.df_dict.setdefault(name, df)

    @staticmethod
    def get_list(node, tag):
        """Get list for pointed child name."""
        return [x.text.rstrip(os.linesep).strip() for x in node.find_all(tag)
                if x is not None]

    def parser_table(self, node, name):
        """Parse BeautifulSoup node to pandas dataframe."""
        df = None
        i = -1
        cols = []
        for child in node.find_all('tr'):
            if child.find('th') is not None:
                cols = self.get_list(child, 'th')
                if cols:
                    df = pandas.DataFrame(columns=cols)
                else:
                    raise ValueError(
                        "Can not find columns for table %s in file %s!",
                        name, self.htmlfile)
            else:
                values = self.get_list(child, 'td')
                i += 1
                if len(values) == len(cols):
                    df.loc[i] = values
                else:
                    raise ValueError(
                        "Values length %s is not same with columns length"
                        " at [%s] line for table %s in file %s!",
                        len(values), i, name, self.htmlfile)
        return df


def test():
    """test."""
    html = Html2Table('ERR004400.html')
    html.parse(['class: zebra run-metatable'])
    print(html.df_dict['class: zebra run-metatable'])

test()
