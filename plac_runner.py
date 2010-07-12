#!python
from __future__ import with_statement
import os, sys, shlex, inspect
import plac

def run(fnames, cmd, verbose):
    "Run batch scripts and tests"
    for fname in fnames:
        with open(fname) as f:
            lines = list(f)
        if not lines[0].startswith('#!'):
            sys.exit('Missing or incorrect shebang line!')
        firstline = lines[0][2:] # strip the shebang
        init_args = shlex.split(firstline)
        tool = plac.import_main(*init_args)
        command = getattr(plac.Interpreter(tool), cmd) # doctest or execute
        if verbose:
            sys.stdout.write('Running %s with %s' % (fname, firstline))
        command(lines[1:], verbose=verbose)

@plac.annotations(
    verbose=('verbose mode', 'flag', 'v'),
    interactive=('run plac tool in interactive mode', 'flag', 'i'),
    batch=('run plac batch files', 'flag', 'b'),
    test=('run plac test files', 'flag', 't'),
    fname='script to run (.py or .plac or .placet)',
    extra='additional arguments',
    )
def main(verbose, interactive, batch, test, fname=None, *extra):
    "Runner for plac tools, plac batch files and plac tests"
    baseparser = plac.parser_from(main)
    if fname is None:
        baseparser.print_help()
    elif sys.argv[1] == fname: # script mode
        plactool = plac.import_main(
            fname, prog=os.path.basename(sys.argv[0]) + ' ' + fname)
        out = plac.call(plactool, sys.argv[2:], eager=False)
        if plac.iterable(out):
            for output in out:
                print(output)
        else:
            print(out)
    elif interactive:
        plactool = plac.import_main(fname, *extra, **{'prog': ''})
        if inspect.isclass(plactool): # special case
            plactool = plactool()
        plac.Interpreter(plactool).interact(verbose=verbose)
    elif batch:
        run((fname,) + extra, 'execute', verbose)
    elif test:
        run((fname,) + extra, 'doctest', verbose)
        print('run %s plac test(s)' % (len(extra) + 1))
    else:
        baseparser.print_usage()
main.add_help = False

if __name__ == '__main__':
    plac.call(main)
