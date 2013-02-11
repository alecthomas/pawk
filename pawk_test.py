import timeit
from pawk import Action, Context, run, parse_commandline
from StringIO import StringIO


TEST_INPUT_LS = r'''
total 72
-rw-r-----  1 alec  staff    18 Feb  9 11:52 MANIFEST.in
-rw-r-----@ 1 alec  staff  3491 Feb 10 11:08 README.md
drwxr-x---  4 alec  staff   136 Feb  9 23:35 dist/
-rwxr-x---  1 alec  staff    53 Feb 10 04:47 pawk*
drwxr-x---  6 alec  staff   204 Feb  9 21:09 pawk.egg-info/
-rw-r-----  1 alec  staff  5045 Feb 10 11:37 pawk.py
-rw-r--r--  1 alec  staff   521 Feb 10 04:56 pawk_test.py
-rw-r-----  1 alec  staff   468 Feb 10 04:42 setup.py
'''


def run_integration_test(input, args):
    input = StringIO(input.strip())
    output = StringIO()
    run(['pawk'] + args, input, output)
    return output.getvalue().strip()


def test_action_parse():
    negate, pattern, cmd = Action()._parse_command(r'/(\w+)/ l')
    assert pattern == r'(\w+)'
    assert cmd == 'l'
    assert negate is False


def test_action_match():
    action = Action(r'(\w+) \w+')
    groups = action._match('test case')
    assert groups == ('test',)


def test_action_match_negate():
    action = Action(r'(\w+) \w+', negate=True)
    groups = action._match('test case')
    assert groups is None
    groups = action._match('test')
    assert groups == ()


def test_integration_sum():
    out = run_integration_test(TEST_INPUT_LS, ['-sBc = 0', '-Ec', 'c += int(f[4])'])
    assert out == '9936'


def test_integration_match():
    out = run_integration_test(TEST_INPUT_LS, ['/pawk_test/ f[4]'])
    assert out == '521'


def test_integration_negate_match():
    out = run_integration_test(TEST_INPUT_LS, ['!/^total|pawk/ f[-1]'])
    assert out.splitlines() == ['MANIFEST.in', 'README.md', 'dist/', 'setup.py']


def test_integration_truth():
    out = run_integration_test(TEST_INPUT_LS, ['int(f[4]) > 1024'])
    assert [r.split()[-1] for r in out.splitlines()] == ['README.md', 'pawk.py']


def test_integration_multiple_actions():
    out = run_integration_test(TEST_INPUT_LS, ['/setup/', '/README/'])
    assert [r.split()[-1] for r in out.splitlines()] == ['README.md', 'setup.py']


def benchmark_fields():
    options, _ = parse_commandline([''])
    action = Action(cmd='f')
    context = Context.from_options(options, [])
    t = timeit.Timer(lambda: action.apply(context, 'foo bar waz was haz has hair'))
    print t.repeat(repeat=3, number=100000)


if __name__ == '__main__':
    benchmark_fields()
