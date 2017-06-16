import argparse

parser = argparse.ArgumentParser(prog="competitive-cli", description="Allows easy access to websites like uva online \
                                                                      judge and codechef from the command line")

subparser = parser.add_subparsers()
uva_parser = subparser.add_parser("uva", help="CLI commands for uva online judge")
codechef_parser = subparser.add_parser("codechef", help="CLI commands for codechef")
template_parser = subparser.add_parser("tpl", help="Manage template files")

# uva_parser.add_argument("uva", choices=["login", "create", "view", "submit", "solutions", "debug"])

uva_parser.add_argument("login", choices=["login new", "login update", "login delete"])
# uva_parser.add_argument("create", )



# print(parser.print_help())
args = parser.parse_args()
print(args)