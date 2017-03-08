import sys
import argparse
import subprocess


SEPARATOR = "#_#"
FORMAT = "--format={{status}}{0}{{path}}{0}{{revid}}{0}{{srccmpath}}{0}\
{{dstcmpath}}{0}{{type}}{0}{{date}}".format(SEPARATOR)
DATEFORMAT = "--dateformat=yyyy-MM-dd'T'HH:mm:ss"


def is_branch_spec(spec):
    return spec.startswith("br:")


def is_cset_spec(spec):
    return spec.startswith("cs:")


def check_valid_spec(spec):
    if is_branch_spec(spec) or is_cset_spec(spec):
        return
    print("Invalid object spec: {}".format(spec), file=sys.stderr)
    sys.exit(1)


def check_valid_arguments(args):
    check_valid_spec(args.first)
    if args.second is None:
        return

    if is_branch_spec(args.first):
        print("A branch cannot be the source of a diff.", file=sys.stderr)
        sys.exit(1)

    if is_cset_spec(args.second):
        return
    print("Invalid destination spec: {}".format(args.second), file=sys.stderr)


def get_valid_args():
    parser = argparse.ArgumentParser(
        description="Create a patch from Plastic SCM changesets or branches")
    parser.add_argument(
        "first",
        help="The changeset or branch to diff, if this is the only present \
    argument. If there are two arguments, this one must be the source \
    changeset.")
    parser.add_argument(
        "second",
        nargs="?",
        help="The destination changeset to diff (optional).")
    parser.add_argument(
        "--compare",
        required=False,
        help="Select what blank characters to recognise.",
        choices=["none", "all", "spaces", "eol"])
    args = parser.parse_args()

    check_valid_arguments(args)
    return args


def main():
    args = get_valid_args()
    diff_args = ["cm", "diff", FORMAT, DATEFORMAT, args.first]

    if args.second is not None:
        diff_args.append(args.second)

    diff_result = subprocess.run(
        diff_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="UTF8")

    if diff_result.returncode != 0:
        print("Unable to build patch contents!", file=sys.stderr)
        print("", file=sys.stderr)
        print(diff_result.stdout, file=sys.stderr)
        sys.exit(1)

    for line in diff_result.stdout.strip().split():
        print("[-]: {}".format(line))


if __name__ == "__main__":
    main()
