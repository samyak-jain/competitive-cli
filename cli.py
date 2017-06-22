import argparse
import pathlib

parser = argparse.ArgumentParser(prog="competitive-cli", description="Allows easy access to websites like uva online \
                                                                      judge and codechef from the command line")

pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

common_parser = argparse.ArgumentParser(add_help=False)
sub_common = common_parser.add_subparsers()

login_parser = sub_common.add_parser("login")
create_parser = sub_common.add_parser("create")
view_parser = sub_common.add_parser("view")
submit_parser = sub_common.add_parser("submit")
download_parser = sub_common.add_parser("download")

sub_parsers = parser.add_subparsers()

uva_parser = sub_parsers.add_parser("uva", parents=[common_parser])
codechef_parser = sub_parsers.add_parser("codechef", parents=[common_parser])
config_parser = sub_parsers.add_parser("config")

config_sub_parser = config_parser.add_subparsers()

template_parser = config_sub_parser.add_parser("tpl")
setb_parser = config_sub_parser.add_parser("set-browser")
setm_parser = config_sub_parser.add_parser("set-mode")
accounts_parser = config_sub_parser.add_parser("accounts")

template_parser.add_argument("view")
tpl_sub = template_parser.add_subparsers()
tpl_create = tpl_sub.add_parser("create")
tpl_delete = tpl_sub.add_parser("delete")
tpl_set = tpl_sub.add_parser("set")


args = parser.parse_args()
