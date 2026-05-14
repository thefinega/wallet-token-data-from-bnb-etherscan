#author: @thefinega

from url import get_url
from value import value
from write import write_file

def main():
    connect=get_url()
    print("\nList of tokens in the wallet: ", value(connect), sep="\n")
    write_file(value(connect))
main()
